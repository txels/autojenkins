import optparse

from autojenkins import Jenkins


def create_opts_parser(command, params="[jobname] [options]"):
    """
    Create parser for command-line options
    """
    usage = "Usage: %prog host " + params
    desc = 'Run autojenkins to {0}.'.format(command)
    parser = optparse.OptionParser(description=desc, usage=usage)
    return parser


def get_variables(options):
    """
    Read all variables and values from ``-Dvariable=value`` options
    """
    split_eq = lambda x: x.split('=')
    data = dict(map(split_eq, options.D))
    return data


def create_job(host, jobname, options):
    """
    Create a new job
    """
    data = get_variables(options)

    print ("""
    Creating job '{0}' from template '{1}' with:
      {2}
    """.format(jobname, options.template, data))

    jenkins = Jenkins(host)
    response = jenkins.create_copy(jobname, options.template, **data)
    if response.status_code == 200 and options.build:
        print('Triggering build.')
        jenkins.build(jobname)
    return response.status_code


def delete_job(host, jobname):
    """
    Delete an existing job
    """
    print ("Deleting job '{0}'".format(jobname))

    jenkins = Jenkins(host)
    response = jenkins.delete(jobname)
    print('Status: {0}'.format(response.status_code))

def list_jobs(host):
    """
    List all jobs
    """
    COLOR = "\033[{0}m"
    COLORCODE = { 
        'blue': '1;34', 
        'red': '1;31', 
        'yellow': '1;33', 
        'aborted': '1;37',
        'disabled': '0;37',
        'grey': '1;37',
    }

    print ("All jobs in {0}".format(host))
    jenkins = Jenkins(host)
    jobs = jenkins.all_jobs()
    for name, color in jobs:
        print(COLOR.format(COLORCODE[color.split('_')[0]]) + name)

