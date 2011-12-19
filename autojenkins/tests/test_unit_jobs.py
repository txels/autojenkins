from unittest import TestCase

from mock import Mock, patch

from autojenkins.jobs import Jenkins


@patch('autojenkins.jobs.Template')
@patch('autojenkins.jobs.requests')
class TestJenkins(TestCase):

    def setUp(self):
        super(TestJenkins, self).setUp()
        self.jenkins = Jenkins('http://jenkins')

    def test_all_jobs(self, requests, Template):
        response = Mock()
        response.content = "{'jobs':[{'name': 'job1', 'color': 'blue'}]}"
        requests.get.return_value = response
        jobs = self.jenkins.all_jobs()
        requests.get.assert_called_once_with('http://jenkins/api/python',
                                             auth=None)
        self.assertEqual(jobs, [('job1', 'blue')])
