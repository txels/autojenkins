import requests
from jinja2 import Template


API = '/api/python'
NEWJOB = '{0}/createItem'
JOB_URL = '{0}/job/{1}'
DELETE = '{0}/job/{1}/doDelete'
BUILD = '{0}/job/{1}/build'
CONFIG = '{0}/job/{1}/config.xml'
JOBINFO = '{0}/job/{1}' + API
LIST = '{0}' + API
LAST_SUCCESS = '{0}/job/{1}/lastSuccessfulBuild' + API
TEST_REPORT = '{0}/job/{1}/lastSuccessfulBuild/testReport' + API
LAST_BUILD = '{0}/job/{1}/lastBuild' + API
LAST_REPORT = '{0}/job/{1}/lastBuild/testReport' + API
ENABLE = '{0}/job/{1}/enable'
DISABLE = '{0}/job/{1}/disable'


class Jenkins(object):
    """Main class to interact with a Jenkins server."""

    def __init__(self, base_url, auth=None):
        self.ROOT = base_url
        self.auth = auth

    def _build_url(self, command, *args):
        """
        Build the proper Jenkins URL for the command.
        """
        return command.format(self.ROOT, *args)

    def _other_url(self, root, command, *args):
        """
        Build the proper Jenkins URL for the command.
        """
        return command.format(root, *args)

    def _get(self, url_pattern, *args):
        return requests.get(self._build_url(url_pattern, *args),
                            auth=self.auth)

    def _post(self, url_pattern, *args):
        return requests.post(self._build_url(url_pattern, *args),
                            auth=self.auth)

    def all_jobs(self):
        """
        Get a list of tuples with (name, color) of all jobs in the server.

        Color is ``blue``, ``yellow`` or ``red`` depending on build results
        (SUCCESS, UNSTABLE or FAILED).
        """
        response = self._get(LIST)
        jobs = eval(response.content).get('jobs', [])
        return [(job['name'], job['color']) for job in jobs]

    def job_url(self, jobname):
        """
        Get the human-browseable URL for a job.
        """
        return self._build_url(JOB_URL, jobname)

    def job_info(self, jobname):
        """
        Get all information for a job as a Python object (dicts & lists).
        """
        response = self._get(JOBINFO, jobname)
        return eval(response.content)

    def last_build_info(self, jobname):
        """
        Get information for last build of a job.
        """
        response = self._get(LAST_BUILD, jobname)
        return eval(response.content)

    def last_build_report(self, jobname):
        """
        Get full report of last build.
        """
        response = self._get(LAST_REPORT, jobname)
        return eval(response.content)

    def last_result(self, jobname):
        """
        Obtain results from last execution.
        """
        last_result_url = self.job_info(jobname)['lastBuild']['url']
        response = requests.get(last_result_url + API, auth=self.auth)
        return eval(response.content)

    def last_success(self, jobname):
        """
        Return information about the last successful build.
        """
        response = self._get(LAST_SUCCESS, jobname)
        return eval(response.content)

    def get_config_xml(self, jobname):
        """
        Get the ``config.xml`` file that contains the job definition.
        """
        response = self._get(CONFIG, jobname)
        return response.content

    def set_config_xml(self, jobname, config):
        """
        Update the ``config.xml`` of a existing job.
        """
        return requests.post(self._build_url(CONFIG, jobname),
                             data=config,
                             headers={'Content-Type': 'application/xml'},
                             auth=self.auth)

    def create(self, jobname, config_file, **context):
        """
        Create a job from a configuration file.
        """
        params = {'name': jobname}
        with open(config_file) as file:
            content = file.read()

        template = Template(content)
        content = template.render(**context)

        return requests.post(self._build_url(NEWJOB),
                             data=content,
                             params=params,
                             headers={'Content-Type': 'application/xml'},
                             auth=self.auth)

    def create_copy(self, jobname, template_job, enable=True, **context):
        """
        Create a job from a template job.
        """
        config = self.get_config_xml(template_job)

        # remove stupid quotes added by Jenkins
        config = config.replace('>&quot;{{', '>{{')
        config = config.replace('}}&quot;<', '}}<')

        template_config = Template(config)
        config = template_config.render(**context)
        if enable:
            config = config.replace('<disabled>true</disabled>',
                                    '<disabled>false</disabled>')

        return requests.post(self._build_url(NEWJOB),
                             data=config,
                             params={'name': jobname},
                             headers={'Content-Type': 'application/xml'},
                             auth=self.auth)

    def transfer(self, jobname, to_server):
        """
        Copy a job to another server.
        """
        config = self.get_config_xml(jobname)
        return requests.post(self._other_url(to_server, NEWJOB),
                             data=config,
                             params={'name': jobname},
                             headers={'Content-Type': 'application/xml'},
                             auth=self.auth)

    def copy(self, jobname, copy_from='template'):
        """
        Copy a job from another one (by default from one called ``template``).
        """
        params = {'name': jobname, 'mode': 'copy', 'from': copy_from}
        return requests.post(self._build_url(NEWJOB), params=params,
                             auth=self.auth)

    def build(self, jobname):
        """
        Trigger Jenkins to build a job.
        """
        return self._post(BUILD, jobname)

    def delete(self, jobname):
        """
        Delete a job.
        """
        return self._post(DELETE, jobname)

    def enable(self, jobname):
        """
        Trigger Jenkins to enable a job.
        """
        return self._post(ENABLE, jobname)

    def disable(self, jobname):
        """
        Trigger Jenkins to disable a job.
        """
        return self._post(DISABLE, jobname)
