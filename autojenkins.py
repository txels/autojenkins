import requests

ROOT = 'http://jenkins.pe.local/'

API = '/api/python'
BUILD   = ROOT + 'job/{0}/build'
CONFIG  = ROOT + 'job/{0}/config.xml'
NEWJOB  = ROOT + 'createItem'
JOBINFO = ROOT + 'job/{0}' + API
LAST_SUCCESS = ROOT + 'job/{0}/lastSuccessfulBuild' + API
TEST_REPORT  = ROOT + 'job/{0}/lastSuccessfulBuild/testReport' + API


def build(jobname):
    url = BUILD.format(jobname)
    return requests.post(url)

def job_info(jobname):
    url = JOBINFO.format(jobname)
    response = requests.get(url)
    return eval(response.content)

def new_job(jobname):
    params = { 'name': jobname, 'mode': 'copy', 'from': 'template' }
    return requests.post(NEWJOB, params=params)

def get_config_xml(jobname):
    url = CONFIG.format(jobname)
    response = requests.get(url)
    return response.content
