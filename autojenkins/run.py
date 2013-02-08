"""Autojenkins CLI

Usage:
  autojenkins list <host> [(--user=<USER> --password=<PASSWORD>)] [--proxy=<PROXY>][-nr]
  autojenkins create <jobname> <host> <template> [(--user=<USER> --password=<PASSWORD>)] [--build][--proxy=<PROXY>]
  autojenkins build <jobname> <host> [(--user=<USER> --password=<PASSWORD>)][--wait][--proxy=<PROXY>]
  autojenkins delete <host> <jobname>... [(--user=<USER> --password=<PASSWORD>)][--proxy=<PROXY>]
  autojenkins --version
  autojenkins -h | --help

Options:
  -h, --help               show this help message and exit
  --version                Show version
  -u USER, --user=USER     username
  -p PASSWORD, --password=PASSWORD
                           password or API token
  -x, --proxy=PROXY        Proxyserver (Host:Port)
  -b, --build              start build after creation
  -w, --wait               wait until the build completes
  -n, --no-color           do not use colored output
  -r, --raw                print raw list of jobs

"""

import optparse
import sys
from docopt import docopt

from autojenkins import Jenkins, jobs

COLOR_MEANING = {
    'blue': ('1;32', 'SUCCESS'),
    'green': ('1;32', 'SUCCESS'),
    'red': ('1;31', 'FAILED'),
    'yellow': ('1;33', 'UNSTABLE'),
    'aborted': ('1;37', 'ABORTED'),
    'disabled': ('0;37', 'DISABLED'),
    'grey': ('1;37', 'NOT BUILT'),
}
# [(--user=<USER> --password=<PASSWORD>)] [--proxy=<PROXY>] [-nr]

def create_opts_parser(command, params="[jobname] [options]"):
    """
    Create parser for command-line options
    """
    usage = "Usage: %prog host " + params
    desc = 'Run autojenkins to {0}.'.format(command)
    parser = optparse.OptionParser(description=desc, usage=usage)
    parser.add_option('-u', '--user',
                      help='username')
    parser.add_option('-p', '--password',
                      help='password or token')
    parser.add_option('-x', '--proxy',
                      help='proxy server (host:port)')
    return parser


def get_variables(options):
    """
    Read all variables and values from ``-Dvariable=value`` options
    """
    split_eq = lambda x: x.split('=')
    data = dict(map(split_eq, options.D))
    return data

def get_proxy(args):
    """
    Return a proxy dictionary
    """
    if args['--proxy'] == None:
        return { "http"  : "", "https" : "" }
    else:
        return { "http"  : args['--proxy'], "https" : args['--proxy'] }

def get_auth(args):
    """
    Return a tuple of (user, password) or None if no authentication
    """
    if args['--user'] == None:
        return None
    else:
        return (args['--user'], args['--password'])


def create_job(host, jobname, options):
    """
    Create a new job
    """
    data = get_variables(options)

    print ("""
    Creating job '{0}' from template '{1}' with:
      {2}
    """.format(jobname, options.template, data))

    jenkins = Jenkins(host, proxies=get_proxy(options), auth=get_auth(options))
    response = jenkins.create_copy(jobname, options.template, **data)
    if response.status_code == 200 and options.build:
        print('Triggering build.')
        jenkins.build(jobname)
    print ('Job URL: {0}'.format(jenkins.job_url(jobname)))
    return response.status_code


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
    response = jenkins.build(jobname, wait=options.wait)
    if options.wait:
        result = response['result']
        print('Result = "{0}"'.format(result))
        return result == 'SUCCESS'
    else:
        return response.status_code < 400


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
                print "Job '%s' deleted" % jobname
        except jobs.JobInexistent as error:
            print "Error: %s" % error.msg
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
    jobs = jenkins.all_jobs()
    for name, color in jobs:
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
        args = docopt(__doc__, version='autojenkins 0.9.0-docopt')
        if args['list']:
            list_jobs(args['<host>'], args, not args['--no-color'], args['--raw'])
        elif args['delete']:
            delete_jobs(args['<host>'], args['<jobname>'], args)
    @staticmethod
    def create():
        parser = create_opts_parser('create a job')
        parser.add_option('-D', metavar='VAR=VALUE',
                          action="append",
                          help='substitution variables to be used in the '
                               'template')
        parser.add_option('-t', '--template', default='template',
                          help='the template job to copy from')
        parser.add_option('-b', '--build',
                          action="store_true", dest="build", default=False,
                          help='start a build right after creation')

        (options, args) = parser.parse_args()

        if len(args) == 2:
            host, jobname = args
            create_job(host, jobname, options)
        else:
            parser.print_help()

    @staticmethod
    def build():
        parser = create_opts_parser('build a job')
        parser.add_option('-w', '--wait',
                          action="store_true", dest="wait", default=False,
                          help='wait until the build completes')

        (options, args) = parser.parse_args()

        if len(args) == 2:
            host, jobname = args
            success = build_job(host, jobname, options)
            if not success:
                sys.exit(1)
        else:
            parser.print_help()
