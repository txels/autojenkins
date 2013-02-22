from mock import Mock, patch
from nose.tools import assert_equals

from autojenkins.run import delete_jobs


@patch('autojenkins.run.Jenkins')
def test_delete_jobs(jenkins):
    jenkins.return_value = Mock()
    delete_jobs('http://jenkins', ['hello', 'bye'], None)
    jenkins.assert_called_with('http://jenkins',
                               proxies={'http': '', 'https': ''}, auth=None)
    assert_equals(2, jenkins.return_value.delete.call_count)
    assert_equals(
        [(('hello',), {}), (('bye',), {})],
        jenkins.return_value.delete.call_args_list)


@patch('autojenkins.run.Jenkins')
@patch('autojenkins.jobs.Jenkins.job_exists')
def test_delete_jobs_authenticated(job_exists, jenkins):
    job_exists.return_value = True
    jenkins.return_value = Mock()
    options = {}
    options['--user'] = 'carles'
    options['--password'] = 'secret'
    options['--proxy'] = ''
    delete_jobs('http://jenkins', ['hello'], options)
    jenkins.assert_called_with('http://jenkins', auth=('carles', 'secret'),
                               proxies={'http': '', 'https': ''})
    assert_equals(1, jenkins.return_value.delete.call_count)
    assert_equals(
        [(('hello',), {})],
        jenkins.return_value.delete.call_args_list)
