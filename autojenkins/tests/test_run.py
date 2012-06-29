from mock import Mock, patch
from nose.tools import assert_equals

from autojenkins.run import delete_jobs


@patch('autojenkins.run.Jenkins')
def test_delete_jobs(jenkins):
    jenkins.return_value = Mock()
    delete_jobs('http://jenkins', ['hello', 'bye'])
    jenkins.assert_called_with('http://jenkins')
    assert_equals(2, jenkins.return_value.delete.call_count)
    assert_equals(
            [(('hello',), {}), (('bye',), {})],
            jenkins.return_value.delete.call_args_list)



