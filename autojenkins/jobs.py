import sys
import time
import requests
from jinja2 import Template


class AutojenkinsError(Exception):
    pass


class JobInexistent(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class JobExists(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class JobNotBuildable(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

API = 'api/python'
NEWJOB = '{0}/createItem'
JOB_URL = '{0}/job/{1}'
DELETE = '{0}/job/{1}/doDelete'
BUILD = '{0}/job/{1}/build'
BUILD_WITH_PARAMS = '{0}/job/{1}/buildWithParameters'
CONFIG = '{0}/job/{1}/config.xml'
JOBINFO = '{0}/job/{1}/' + API
BUILDINFO = '{0}/job/{1}/{2}/' + API
LIST = '{0}/' + API
LAST_SUCCESS = '{0}/job/{1}/lastSuccessfulBuild/' + API
TEST_REPORT = '{0}/job/{1}/lastSuccessfulBuild/testReport/' + API
LAST_BUILD = '{0}/job/{1}/lastBuild/' + API
LAST_REPORT = '{0}/job/{1}/lastBuild/testReport/' + API
CONSOLE_TEXT = '{0}/job/{1}/{2}/consoleText'
ENABLE = '{0}/job/{1}/enable'
DISABLE = '{0}/job/{1}/disable'
CONSOLE = '{0}/job/{1}/{2}/consoleText'


class HttpStatusError(Exception):
    pass


class HttpUnauthorized(Exception):
    pass


class HttpForbidden(Exception):
    pass


class HttpNotFoundError(HttpStatusError):
    pass


HTTP_ERROR_MAP = {
    401: HttpUnauthorized,  # credentials wrong
    403: HttpForbidden,  # insufficient rights
    404: HttpNotFoundError
}


def _validate(response):
    """
    Verify the status code of the response and raise exception on codes > 400.
    """
    message = 'HTTP Status: {0}'.format(response.status_code)
    if response.status_code >= 400:
        exception_cls = HTTP_ERROR_MAP.get(response.status_code,
                                           HttpStatusError)
        raise exception_cls(message)
    return response


class Jenkins(object):
    """Main class to interact with a Jenkins server."""

    def __init__(self, base_url, auth=None, verify_ssl_cert=True, proxies={}):
        self.ROOT = base_url
        self.auth = auth
        self.verify_ssl_cert = verify_ssl_cert
        self.proxies = proxies

    def _url(self, command, *args):
        """
        Build the proper Jenkins URL for the command.
        """
        return command.format(self.ROOT, *args)

    def _other_url(self, root, command, *args):
        """
        Build the proper Jenkins URL for the command.
        """
        return command.format(root, *args)

    def _http_get(self, url, **kwargs):
        """
        Perform an HTTP GET request.

        This will add required authentication and SSL verification arguments.
        """
        response = requests.get(url,
                                auth=self.auth,
                                verify=self.verify_ssl_cert,
                                proxies=self.proxies,
                                **kwargs)
        return _validate(response)

    def _http_post(self, url, **kwargs):
        """
        Perform an HTTP POST request.

        This will add required authentication and SSL verification arguments.
        """
        response = requests.post(url,
                                 auth=self.auth,
                                 verify=self.verify_ssl_cert,
                                 proxies=self.proxies,
                                 **kwargs)
        return _validate(response)

    def _build_get(self, url_pattern, *args, **kwargs):
        """
        Build proper URL from pattern and args, and perform an HTTP GET.
        """
        return self._http_get(self._url(url_pattern, *args), **kwargs)

    def _build_post(self, url_pattern, *args, **kwargs):
        """
        Build proper URL from pattern and args, and perform an HTTP POST.
        """
        return self._http_post(self._url(url_pattern, *args), **kwargs)

    def all_jobs(self):
        """
        Get a list of tuples with (name, color) of all jobs in the server.

        Color is ``blue``, ``yellow`` or ``red`` depending on build results
        (SUCCESS, UNSTABLE or FAILED).
        """
        response = self._build_get(LIST)
        jobs = eval(response.text).get('jobs', [])
        return [(job['name'], job['color']) for job in jobs]

    def job_exists(self, jobname):
        jobs = self.all_jobs()
        for (name, color) in jobs:
            if name == jobname:
                return True

    def job_url(self, jobname):
        """
        Get the human-browseable URL for a job.
        """
        return self._url(JOB_URL, jobname)

    def job_info(self, jobname):
        """
        Get all information for a job as a Python object (dicts & lists).
        """
        response = self._build_get(JOBINFO, jobname)
        return eval(response.text)

    def build_info(self, jobname, build_number=None):
        """
        Get information for a build of a job.

        If no build number is specified, defaults to the most recent build.
        """
        if build_number is not None:
            args = (BUILDINFO, jobname, build_number)
        else:
            args = (LAST_BUILD, jobname)
        response = self._build_get(*args)
        return eval(response.text)

    def build_console(self, jobname, build_number=None):
        """
        Get the console output for the build of a job.

        If no build number is specified, defaults to the most recent build.
        """
        if build_number is not None:
            args = (CONSOLE, jobname, build_number)
        else:
            args = (CONSOLE, jobname, "lastBuild")
        response = self._build_get(*args)
        return response.text

    def last_build_console(self, jobname):
        """
        Get the console output for the last build of a job.
        """
        return self.build_console(jobname)

    def last_build_info(self, jobname):
        """
        Get information for last build of a job.
        """
        return self.build_info(jobname)

    def last_build_report(self, jobname):
        """
        Get full report of last build.
        """
        response = self._build_get(LAST_REPORT, jobname)
        return eval(response.text)

    def console_text(self, jobname, build_number='lastBuild'):
        """
        Get console text output of last build.
        """
        response = self._build_get(CONSOLE_TEXT, jobname, build_number)
        return response.content

    def last_result(self, jobname):
        """
        Obtain results from last execution.
        """
        last_result_url = self.job_info(jobname)['lastBuild']['url']
        response = self._http_get(last_result_url + API)
        return eval(response.text)

    def last_success(self, jobname):
        """
        Return information about the last successful build.
        """
        response = self._build_get(LAST_SUCCESS, jobname)
        return eval(response.text)

    def get_config_xml(self, jobname):
        """
        Get the ``config.xml`` file that contains the job definition.
        """
        response = self._build_get(CONFIG, jobname)
        return response.text

    def set_config_xml(self, jobname, config):
        """
        Replace the ``config.xml`` of an existing job.
        """
        return self._build_post(CONFIG, jobname,
                                data=config,
                                headers={'Content-Type': 'application/xml'})

    def create(self, jobname, config_file, **context):
        """
        Create a job from a configuration file.
        """
        params = {'name': jobname}
        with open(config_file) as file:
            content = file.read()

        template = Template(content)
        content = template.render(**context)

        if self.job_exists(jobname):
            raise Exception("Job already exists")
        else:
            return self._build_post(NEWJOB,
                                    data=content,
                                    params=params,
                                    headers={'Content-Type': 'application/xml'}
                                    )

    def create_copy(self, jobname, template_job, enable=True, _force=False, **context):
        """
        Create a job from a template job.
        """
        if not self.job_exists(template_job):
            raise JobInexistent("Template job '%s' doesn't exists" % template_job)

        target_job_exists = self.job_exists(jobname)

        if not _force and target_job_exists:
            raise JobExists("Another job with the name '%s'already exists"
                            % jobname)

        config = self.get_config_xml(template_job)

        # remove stupid quotes added by Jenkins
        config = config.replace('>&quot;{{', '>{{')
        config = config.replace('}}&quot;<', '}}<')

        template_config = Template(config)

        config = template_config.render(**context)
        if enable:
            config = config.replace('<disabled>true</disabled>',
                                    '<disabled>false</disabled>')

        if target_job_exists:
            return self.set_config_xml(jobname, config)
        else:
            return self._build_post(NEWJOB,
                                    data=config,
                                    params={'name': jobname},
                                    headers={'Content-Type': 'application/xml'})

    def transfer(self, jobname, to_server):
        """
        Copy a job to another server.
        """
        config = self.get_config_xml(jobname)
        return self._http_post(self._other_url(to_server, NEWJOB),
                               data=config,
                               params={'name': jobname},
                               headers={'Content-Type': 'application/xml'})

    def copy(self, jobname, copy_from='template'):
        """
        Copy a job from another one (by default from one called ``template``).
        """
        params = {'name': jobname, 'mode': 'copy', 'from': copy_from}
        return self._build_post(NEWJOB, params=params)

    def build(self, jobname, params=None, wait=False, grace=10):
        """
        Trigger Jenkins to build a job.

        :param params:
            If params are provided, use the "buildWithParameters" endpoint
        :param wait:
            If ``True``, wait until job completes building before returning
        """
        if not self.job_exists(jobname):
            raise JobInexistent("Job '%s' doesn't exists" % jobname)
        if not self.job_info(jobname)['buildable']:
            raise JobNotBuildable("Job '%s' is not buildable (deactivated)."
                                  % jobname)
        url_pattern = BUILD if params is None else BUILD_WITH_PARAMS
        response = self._build_post(url_pattern, jobname, params=params)
        if not wait:
            return response
        else:
            time.sleep(grace)
            self.wait_for_build(jobname)
            return self.last_result(jobname)

    def delete(self, jobname):
        """
        Delete a job.
        """
        if self.job_exists(jobname):
            return self._build_post(DELETE, jobname)
        else:
            raise JobInexistent("Job '%s' doesn't exist" % jobname)

    def enable(self, jobname):
        """
        Trigger Jenkins to enable a job.
        """
        return self._build_post(ENABLE, jobname)

    def disable(self, jobname):
        """
        Trigger Jenkins to disable a job.
        """
        return self._build_post(DISABLE, jobname)

    def is_building(self, jobname):
        """
        Check if a job is building
        """
        return self.last_result(jobname).get('building', True)

    def wait_for_build(self, jobname, poll_interval=3):
        """
        Wait until job has finished building
        """
        while (self.is_building(jobname)):
            time.sleep(poll_interval)
            sys.stdout.write('.')
            sys.stdout.flush()
        print('')
