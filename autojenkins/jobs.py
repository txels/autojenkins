import requests
from jinja2 import Template


API = '/api/python'
DELETE = '{0}/job/{1}/doDelete'
BUILD = '{0}/job/{1}/build'
CONFIG = '{0}/job/{1}/config.xml'
NEWJOB = '{0}/createItem'
JOBINFO = '{0}/job/{1}' + API
LAST_SUCCESS = '{0}/job/{1}/lastSuccessfulBuild' + API
TEST_REPORT = '{0}/job/{1}/lastSuccessfulBuild/testReport' + API


class Jenkins(object):

    def __init__(self, base_url):
        self.ROOT = base_url

    def _build_url(self, command, *args):
        """
        Build the proper Jenkins URL for the command.
        """
        return command.format(self.ROOT, *args)

    def job_info(self, jobname):
        """
        Get all information for a job as a Python object (dicts & lists).
        """
        response = requests.get(self._build_url(JOBINFO, jobname))
        return eval(response.content)

    def get_config_xml(self, jobname):
        """
        Get the ``config.xml`` file that contains the job definition.
        """
        response = requests.get(self._build_url(CONFIG, jobname))
        return response.content

    def build(self, jobname):
        """
        Trigger Jenkins to build a job.
        """
        return requests.post(self._build_url(BUILD, jobname))

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
                             headers={'Content-Type': 'application/xml'})

    def create_copy(self, jobname, template_job, enable=True, **context):
        """
        Create a job from a template job.
        """
        config = self.get_config_xml(template_job)
        # with open('config.xml', 'w') as file:
        #    file.write(config)

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
                             headers={'Content-Type': 'application/xml'})

    def copy(self, jobname, copy_from='template'):
        """
        Copy a job from another one (by default from one called ``template``).
        """
        params = {'name': jobname, 'mode': 'copy', 'from': copy_from}
        return requests.post(self._build_url(NEWJOB), params=params)

    def delete(self, jobname):
        """
        Delete a job.
        """
        return requests.post(self._build_url(DELETE, jobname))

    def last_success(self, jobname):
        """
        Return information about the last successful build.
        """
        return requests.post(self._build_url(LAST_SUCCESS, jobname))

    def last_result(self, jobname):
        """
        Obtain results from last execution.
        """
        last_result_url = self.job_info(jobname)['lastBuild']['url']
        response = requests.get(last_result_url + API)
        return eval(response.content)
