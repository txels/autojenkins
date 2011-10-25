import requests

ROOT = 'http://jenkins.pe.local/'
BUILD = ROOT + 'job/{0}/build'

def build(jobname):
    url = BUILD.format(jobname)
    requests.post(url)

