import optparse

from autojenkins import Jenkins


def create_opts_parser():
    usage = "Usage: %prog host jobname [options]"
    desc = 'Run autojenkins to create a job.'
    parser = optparse.OptionParser(description=desc, usage=usage)
    #parser.add_option('jobname',
    #                    help='the name of a job in jenkins')
    parser.add_option('-D', metavar='PROP=VALUE',
                      action="append",
                      help='substitution variables to be used in the template')
    parser.add_option('-t', '--template', default='template',
                      help='the template job to copy from')
    parser.add_option('-b', '--build',
                      action="store_true", dest="build", default=False,
                      help='start a build right after creation')
    return parser


def run_jenkins(host, jobname, options):
    spliteq = lambda x : x.split('=')
    data = dict(map(spliteq, options.D))

    print ("""
    Creating job '{0}' from template '{1}' with:
      {2}
    """.format(jobname, options.template, data))

    jenkins = Jenkins(host)
    response = jenkins.create_copy(jobname, options.template, **data)
    print('Status: {0}'.format(response.status_code))
    if response.status_code == 200 and options.build:
        print('Triggering build.')
        j.build(jobname)

