import optparse

from autojenkins import Jenkins

COLOR_MEANING = {
    'blue': ('1;34', 'SUCCESS'),
    'red': ('1;31', 'FAILED'),
    'yellow': ('1;33', 'UNSTABLE'),
    'aborted': ('1;37', 'ABORTED'),
    'disabled': ('0;37', 'DISABLED'),
    'grey': ('1;37', 'NOT BUILT'),
}


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


def list_jobs(host, color=True):
    """
    List all jobs
    """
    if color:
        FORMAT = "\033[{0}m{1}\033[0m"
        position = 0
    else:
        FORMAT = "{0:<10} {1}"
        position = 1
    print ("All jobs in {0}".format(host))
    jenkins = Jenkins(host)
    jobs = jenkins.all_jobs()
    for name, color in jobs:
        if '_' in color:
            color = color.split('_')[0]
            building = True
        else:
            building = False
        prefix = '* ' if building else '  '
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
    def delete():
        parser = create_opts_parser('delete a job')

        (options, args) = parser.parse_args()

        if len(args) == 2:
            host, jobname = args
            delete_job(host, jobname)
        else:
            parser.print_help()

    @staticmethod
    def list():
        parser = create_opts_parser('list all jobs', params='')
        parser.add_option('-n', '--no-color',
                          action="store_true", dest="color", default=False,
                          help='do not use colored output')

        (options, args) = parser.parse_args()

        if len(args) == 1:
            host, = args
            list_jobs(host, not options.color)
        else:
            parser.print_help()
