import optparse

from autojenkins import Jenkins


def create_opts_parser(command):
    """
    Create parser for command-line options
    """
    usage = "Usage: %prog host jobname [options]"
    desc = 'Run autojenkins to {0} a job.'.format(command)
    parser = optparse.OptionParser(description=desc, usage=usage)
    #parser.add_option('jobname',
    #                    help='the name of a job in jenkins')
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
        j.build(jobname)
    return response.status_code


def delete_job(host, jobname):
    """
    Delete an existing job
    """
    print ("Deleting job '{0}'".format(jobname))

    jenkins = Jenkins(host)
    response = jenkins.delete(jobname)
    print('Status: {0}'.format(response.status_code))
