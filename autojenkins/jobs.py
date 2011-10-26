import requests


API = '/api/python'
DELETE = '{0}/job/{1}/doDelete'
BUILD = '{0}/job/{1}/build'
CONFIG = '{0}/job/{1}/config.xml'
NEWJOB = '{0}/createItem'
JOBINFO = '{0}/job/{1}' + API
LAST_SUCCESS = '{0}/job/{1}/lastSuccessfulBuild' + API
TEST_REPORT = '{0}/job/{1}/lastSuccessfulBuild/testReport' + API


class Jenkins(object):

    def __init__(self, base_url='http://jenkins.pe.local'):
        self.ROOT = base_url


    def _build_url(self, command, *args):
        """Build the proper Jenkins URL for the command."""
        return command.format(self.ROOT, *args)


    def build(self, jobname):
        """Trigger Jenkins to build a job."""
        return requests.post(self._build_url(BUILD, jobname))


    def job_info(self, jobname):
        """Get all information for a job as a Python object (dicts & lists)."""
        response = requests.get(self._build_url(JOBINFO, jobname))
        return eval(response.content)


    def copy(self, jobname, copy_from='template'):
        """
        Copy a job from another one (by default from one called ``template``).
        """
        params = {'name': jobname, 'mode': 'copy', 'from': copy_from}
        return requests.post(self._build_url(NEWJOB), params=params)


    def get_config_xml(self, jobname):
        """Get the ``config.xml`` file that contains the full job definition."""
        response = requests.get(self._build_url(CONFIG, jobname))
        return response.content


    def delete(self, jobname):
        """Delete a job."""
        return requests.post(self._build_url(DELETE, jobname))
