"""Autojenkins CLI

Usage:
  autojenkins list <host> [(--user=<USER> --password=<PASSWORD>)]
            [--proxy=<PROXY>][-nr]
  autojenkins create <host> <jobname> <template> [-D=<VAR=VALUE>]... [--build]
            [(--user=<USER> --password=<PASSWORD>)] [--proxy=<PROXY>]
  autojenkins build <host> <jobname> [--wait]
            [(--user=<USER> --password=<PASSWORD>)][--proxy=<PROXY>]
  autojenkins delete <host> <jobname>...
            [(--user=<USER> --password=<PASSWORD>)][--proxy=<PROXY>]
  autojenkins --version
  autojenkins -h | --help

Options:
  -h, --help               show this help message and exit
  --version                Show version
  -u USER, --user=USER     username
  -p PASSWORD, --password=PASSWORD
                           password or API token
  -D VAR=VALUE             substitution variables to be used in the template
  -x, --proxy=PROXY        Proxyserver (Host:Port)
  -b, --build              start build after creation
  -w, --wait               wait until the build completes
  -n, --no-color           do not use colored output
  -r, --raw                print raw list of jobs

"""

from __future__ import print_function

import sys
from docopt import docopt

from ajk_version import __version__
from autojenkins import Jenkins, jobs

COLOR_MEANING = {
    'blue': ('1;32', 'SUCCESS'),
    'green': ('1;32', 'SUCCESS'),
    'red': ('1;31', 'FAILED'),
    'yellow': ('1;33', 'UNSTABLE'),
    'aborted': ('1;37', 'ABORTED'),
    'disabled': ('0;37', 'DISABLED'),
    'grey': ('1;37', 'NOT BUILT'),
    'notbuilt': ('1;37', 'NOT BUILT'),
}


def get_variables(options):
    """
    Read all variables and values from ``-Dvariable=value`` options
    """
    split_eq = lambda x: x.split('=')
    data = dict(map(split_eq, options))
    return data


def get_proxy(args):
    """
    Return a proxy dictionary
    """
    if args is None or args['--proxy'] is None:
        return {"http": "", "https": ""}
    else:
        return {"http": args['--proxy'], "https": args['--proxy']}


def get_auth(args):
    """
    Return a tuple of (user, password) or None if no authentication
    """
    if args is None or args['--user'] is None:
        return None
    else:
        return (args['--user'], args['--password'])


def create_job(host, jobname, options):
    """
    Create a new job
    """
    data = get_variables(options['-D'])

    print ("""
    Creating job '{0}' from template '{1}' with:
      {2}
    """.format(jobname, options['<template>'], data))

    jenkins = Jenkins(host, proxies=get_proxy(options), auth=get_auth(options))
    try:
        response = jenkins.create_copy(jobname, options['<template>'], **data)
        if response.status_code == 200 and options['--build']:
            print('Triggering build.')
            jenkins.build(jobname)
        print ('Job URL: {0}'.format(jenkins.job_url(jobname)))
        return response.status_code < 400
    except jobs.JobExists as error:
        print("Error:", error.msg)
        return False


def build_job(host, jobname, options):
    """
    Trigger build for an existing job.

    If the wait option is specified, wait until build completion

    :returns:

        A boolean value indicating success:

         * If wait: ``True`` if build was successful, ``False`` otherwise
         * If not wait: ``True`` if HTTP status code is not an error code
    """
    print ("Start building job '{0}'".format(jobname))
    jenkins = Jenkins(host, proxies=get_proxy(options), auth=get_auth(options))
    try:
        response = jenkins.build(jobname, wait=options['--wait'])
        if options['--wait']:
            result = response['result']
            print('Result = "{0}"'.format(result))
            return result == 'SUCCESS'
        else:
            print("Build '%s' started" % jobname)
            return response.status_code < 400
    except (jobs.JobInexistent, jobs.JobNotBuildable) as error:
        print("Error:", error.msg)
        return False


def delete_jobs(host, jobnames, options):
    """
    Delete existing jobs.
    """
    jenkins = Jenkins(host, proxies=get_proxy(options), auth=get_auth(options))
    for jobname in jobnames:
        print ("Deleting job '{0}'".format(jobname))
        try:
            response = jenkins.delete(jobname)
            if response.status_code == 200:
                print("Job '%s' deleted" % jobname)
        except jobs.JobInexistent as error:
            print("Error:", error.msg)
            print("Error:", error.msg)
        except (jobs.HttpForbidden, jobs.HttpUnauthorized):
            pass


def list_jobs(host, options, color=True, raw=False):
    """
    List all jobs
    """
    if raw:
        FORMAT = "{1}"
        position = 0
    elif color:
        FORMAT = "\033[{0}m{1}\033[0m"
        position = 0
    else:
        FORMAT = "{0:<10} {1}"
        position = 1
    if not raw:
        print ("All jobs in {0}".format(host))
    jenkins = Jenkins(host, proxies=get_proxy(options), auth=get_auth(options))
    joblist = jenkins.all_jobs()
    for name, color in joblist:
        if '_' in color:
            color = color.split('_')[0]
            building = True
        else:
            building = False
        prefix = '' if raw else '* ' if building else '  '
        out = COLOR_MEANING[color][position]
        print(prefix + FORMAT.format(out, name))


class Commands:
    @staticmethod
    def main():
        args = docopt(__doc__, version=__version__)
        if args['list']:
            list_jobs(args['<host>'], args, not args['--no-color'],
                      args['--raw'])
        elif args['delete']:
            delete_jobs(args['<host>'], args['<jobname>'], args)
        elif args['build']:
            success = build_job(args['<host>'], args['<jobname>'][0], args)
            if not success:
                sys.exit(1)
        elif args['create']:
            success = create_job(args['<host>'], args['<jobname>'][0], args)
            if not success:
                sys.exit(1)
