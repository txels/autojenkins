import optparse
import sys

from autojenkins import Jenkins

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
    return parser


def get_variables(options):
    """
    Read all variables and values from ``-Dvariable=value`` options
    """
    split_eq = lambda x: x.split('=')
    data = dict(map(split_eq, options.D))
    return data


def get_auth(options):
    """
    Return a tuple of (user, password) or None if no authentication
    """
    if hasattr(options, 'user'):
        return (options.user, getattr(options, 'password', None))
    else:
        return None


def create_job(host, jobname, options):
    """
    Create a new job
    """
    data = get_variables(options)

    print ("""
    Creating job '{0}' from template '{1}' with:
      {2}
    """.format(jobname, options.template, data))

    jenkins = Jenkins(host, auth=get_auth(options))
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

    jenkins = Jenkins(host, auth=get_auth(options))
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
    jenkins = Jenkins(host, auth=get_auth(options))
    for jobname in jobnames:
        print ("Deleting job '{0}'".format(jobname))
        response = jenkins.delete(jobname)
        print(response.status_code)


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
    jenkins = Jenkins(host, auth=get_auth(options))
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

    @staticmethod
    def delete():
        parser = create_opts_parser('delete one or more jobs',
                                    params="[jobname]+ [options]")

        (options, args) = parser.parse_args()

        if len(args) >= 2:
            host, jobnames = args[0], args[1:]
            delete_jobs(host, jobnames, options)
        else:
            parser.print_help()

    @staticmethod
    def list():
        parser = create_opts_parser('list all jobs', params='')
        parser.add_option('-n', '--no-color',
                          action="store_true", dest="color", default=False,
                          help='do not use colored output')
        parser.add_option('-r', '--raw',
                          action="store_true", dest="raw", default=False,
                          help='print raw list of jobs')

        (options, args) = parser.parse_args()

        if len(args) == 1:
            host, = args
            list_jobs(host, options, not options.color, options.raw)
        else:
            parser.print_help()
