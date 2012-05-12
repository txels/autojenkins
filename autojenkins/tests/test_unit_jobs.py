from os import path
from unittest import TestCase

from ddt import ddt, data
from mock import Mock, patch

from autojenkins.jobs import Jenkins, HttpNotFoundError, HttpStatusError


fixture_path = path.dirname(__file__)


def load_fixture(name):
    with open(path.join(fixture_path, name)) as f:
        fixture = f.read()
    return fixture


def mock_response(fixture=None, status=200):
    response = Mock()
    if fixture is None:
        response.content = ''
    elif isinstance(fixture, dict):
        response.content = str(fixture)
    else:
        response.content = load_fixture(fixture)
    response.status_code = status
    return response


@ddt
@patch('autojenkins.jobs.Template')
@patch('autojenkins.jobs.requests')
class TestJenkins(TestCase):

    def setUp(self):
        super(TestJenkins, self).setUp()
        self.jenkins = Jenkins('http://jenkins')

    def test_all_jobs(self, requests, Template):
        response = {'jobs': [{'name': 'job1', 'color': 'blue'}]}
        requests.get.return_value = mock_response(response)
        jobs = self.jenkins.all_jobs()
        requests.get.assert_called_once_with('http://jenkins/api/python',
                                             auth=None)
        self.assertEqual(jobs, [('job1', 'blue')])

    def test_get_job_url(self, *args):
        url = self.jenkins.job_url('job123')
        self.assertEqual('http://jenkins/job/job123', url)

    def test_last_result(self, requests, *args):
        second_response = Mock()
        second_response.content = "{'result': 23}"
        requests.get.side_effect = [
            mock_response('job_info.txt'), second_response
        ]
        response = self.jenkins.last_result('name')
        self.assertEqual(23, response['result'])
        self.assertEqual(
            (('https://builds.apache.org/job/Solr-Trunk/1783/api/python',),
             {'auth': None}),
            requests.get.call_args_list[1]
        )

    @data(
        ('job_info', 'job/{0}/api/python'),
        ('last_build_info', 'job/{0}/lastBuild/api/python'),
        ('last_build_report', 'job/{0}/lastBuild/testReport/api/python'),
        ('last_success', 'job/{0}/lastSuccessfulBuild/api/python'),
        ('get_config_xml', 'job/{0}/config.xml'),
    )
    def test_get_methods_with_jobname(self, case, requests, Template):
        method, url = case
        requests.get.return_value = mock_response('{0}.txt'.format(method))
        response = getattr(self.jenkins, method)('name')
        requests.get.assert_called_once_with(
            'http://jenkins/' + url.format('name'),
            auth=None)
        getattr(self, 'checks_{0}'.format(method))(response)

    def check_result(self, response, route, value):
        for key in route:
            response = response[key]
        self.assertEqual(response, value)

    def check_results(self, response, values):
        for route, value in values:
            self.check_result(response, route, value)

    def checks_job_info(self, response):
        self.check_results(response,
            [(('color',), 'red'),
             (('lastSuccessfulBuild', 'number'), 1778),
             (('lastSuccessfulBuild', 'url'),
                            'https://builds.apache.org/job/Solr-Trunk/1778/'),
            ])

    def checks_last_build_info(self, response):
        self.check_results(response,
            [(('timestamp',), 1330941036216L),
             (('number',), 1783),
             (('result',), 'FAILURE'),
             (('changeSet', 'kind'), 'svn'),
            ])

    def checks_last_build_report(self, response):
        self.check_results(response,
            [(('duration',), 692.3089),
             (('failCount',), 1),
             (('suites', 0, 'name'), 'org.apache.solr.BasicFunctionalityTest'),
            ])

    def checks_last_success(self, response):
        self.check_results(response,
            [(('result',), 'SUCCESS'),
             (('building',), False),
             (('artifacts', 0, 'displayPath'),
                        'apache-solr-4.0-2012-02-29_09-07-30-src.tgz'),
            ])

    def checks_get_config_xml(self, response):
        self.assertTrue(response.startswith('<?xml'))
        self.assertTrue(response.endswith('</project>'))

    # TODO: test job creation, and set_config_xml

    @data(
        ('build', 'job/{0}/build'),
        ('delete', 'job/{0}/doDelete'),
        ('enable', 'job/{0}/enable'),
        ('disable', 'job/{0}/disable'),
    )
    def test_post_methods_with_jobname(self, case, requests, Template):
        method, url = case
        # Jenkins API post methods return status 302 upon success
        requests.post.return_value = mock_response(status=302)
        response = getattr(self.jenkins, method)('name')
        self.assertEqual(302, response.status_code)
        requests.post.assert_called_once_with(
            'http://jenkins/' + url.format('name'),
            auth=None)

    @patch('autojenkins.jobs.time')
    @patch('autojenkins.jobs.Jenkins.last_result')
    @patch('autojenkins.jobs.Jenkins.wait_for_build')
    def test_build_with_wait(self, wait_for_build, last_result, time, requests,
            Template):
        """Test building a job synchronously"""
        requests.post.return_value = mock_response(status=302)
        last_result.return_value = {'result': 'HELLO'}
        result = self.jenkins.build('name', wait=True)
        self.assertEqual({'result': 'HELLO'}, result)
        requests.post.assert_called_once_with(
            'http://jenkins/job/name/build',
            auth=None)
        last_result.assert_called_once_with('name')
        time.sleep.assert_called_once_with(10)

    @patch('autojenkins.jobs.time')
    @patch('autojenkins.jobs.sys')
    @patch('autojenkins.jobs.Jenkins.is_building')
    def test_wait_for_build(self, is_building, sys, time, requests, Template):
        is_building.side_effect = [True, True, False]
        self.jenkins.wait_for_build('name')
        self.assertEqual(3, is_building.call_count)
        self.assertEqual(2, time.sleep.call_count)
        self.assertEqual(((3,), {}), time.sleep.call_args)

    def test_404_raises_http_not_found(self, requests, Template):
        http404_response = Mock()
        http404_response.status_code = 404
        requests.get.return_value = http404_response
        with self.assertRaises(HttpNotFoundError):
            self.jenkins.last_build_info('job123')

    def test_500_raises_http_error(self, requests, Template):
        http500_response = Mock()
        http500_response.status_code = 500
        requests.get.return_value = http500_response
        with self.assertRaises(HttpStatusError):
            self.jenkins.last_build_info('job123')
