from os import path
from unittest import TestCase

from ddt import ddt, data
from mock import Mock, patch
from nose.tools import assert_equal

from autojenkins.jobs import Jenkins


fixture_path = path.dirname(__file__)


def load_fixture(name):
    with open(path.join(fixture_path, name)) as f:
        fixture = f.read()
    return fixture


def mock_response(fixture=None):
    response = Mock()
    if fixture is None:
        response.content = "{'jobs':[{'name': 'job1', 'color': 'blue'}]}"
    else:
        response.content = load_fixture(fixture)
    return response


@ddt
@patch('autojenkins.jobs.Template')
@patch('autojenkins.jobs.requests')
class TestJenkins(TestCase):

    def setUp(self):
        super(TestJenkins, self).setUp()
        self.jenkins = Jenkins('http://jenkins')

    def test_all_jobs(self, requests, Template):
        requests.get.return_value = mock_response()
        jobs = self.jenkins.all_jobs()
        requests.get.assert_called_once_with('http://jenkins/api/python',
                                             auth=None)
        self.assertEqual(jobs, [('job1', 'blue')])

    @data(
        ('job_info', 'job/{0}/api/python'),
        ('last_build_info', 'job/{0}/lastBuild/api/python'),
        ('last_build_report', 'job/{0}/lastBuild/testReport/api/python'),
    )
    def test_get_methods_with_jobname(self, case, requests, Template):
        method, url = case
        requests.get.return_value = mock_response('{0}.txt'.format(method))
        info = getattr(self.jenkins, method)('name')
        requests.get.assert_called_once_with(
            'http://jenkins/' + url.format('name'),
            auth=None)
        getattr(self, 'checks_{0}'.format(method))(info)

    def check_result(self, info, route, value):
        for key in route:
            info = info[key]
        self.assertEqual(info, value)

    def check_results(self, info, values):
        for route, value in values:
            self.check_result(info, route, value)

    def checks_job_info(self, info):
        self.check_results(info,
            [(('color',), 'red'),
             (('lastSuccessfulBuild', 'number'), 1778),
             (('lastSuccessfulBuild', 'url'),
                            'https://builds.apache.org/job/Solr-Trunk/1778/'),
            ])

    def checks_last_build_info(self, info):
        self.check_results(info,
            [(('timestamp',), 1330941036216L),
             (('number',), 1783),
             (('result',), 'FAILURE'),
             (('changeSet', 'kind'), 'svn'),
            ])

    def checks_last_build_report(self, info):
        self.check_results(info,
            [(('duration',), 692.3089),
             (('failCount',), 1),
             (('suites', 0, 'name'), 'org.apache.solr.BasicFunctionalityTest'),
            ])
