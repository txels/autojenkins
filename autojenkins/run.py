import optparse

from autojenkins import Jenkins


def create_opts_parser():
    usage = "Usage: %prog jobname [options]"
    desc = 'Run autojenkins to create a job.'
    parser = optparse.OptionParser(description=desc, usage=usage)
    #parser.add_option('jobname',
    #                    help='the name of a job in jenkins')
    parser.add_option('--repo',
                      help='the repository name in github')
    parser.add_option('--branch',
                      help='the branch name')
    parser.add_option('--package',
                      help='the main python package (that contains manage.py)')
    parser.add_option('-t', '--template', default='template',
                      help='the template job to copy from')
    parser.add_option('-b', '--build',
                      action="store_true", dest="build", default=False,
                      help='start a build right after creation')
    return parser


def run_jenkins(jobname, options):
    is_not_none = lambda res, opt: res and getattr(options, opt) is not None
    all_options_ok = reduce(is_not_none, ['repo', 'branch', 'package'])
    if all_options_ok:

        print ("""Creating job '{0}' from template '{1}' for:
    - repo:    {2}
    - branch:  {3}
    - package: {4}
    """.format(jobname, options.template, options.repo, options.branch,
               options.package))

        jenkins = Jenkins('http://jenkins.pe.local')
        response = jenkins.create_copy(jobname, options.template,
                                       repo=options.repo,
                                       branch=options.branch,
                                       package=options.package)
        print('Status: {0}'.format(response.status_code))
        if response.status_code == 200 and options.build:
            print('Triggering build.')
            j.build(jobname)
    return all_options_ok

