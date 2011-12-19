from datetime import datetime

from autojenkins import Jenkins


if __name__ == '__main__':
    """
    j = Jenkins('http://jenkins.pe.local')
    # dir = path.dirname(path.dirname(__file__))
    # config_file = path.join(dir, 'templates/story-dev-job.xml')
    response = j.delete('aaa')
    response = j.create_copy('aaa', 'template',
                             repo='mbf-warehouse-screens',
                             branch='us544_login',
                             package='warehouse_screens')
    print(response.status_code)
    if response.status_code == 200:
        j.build('aaa')
    """
    # j = Jenkins('https://builds.apache.org')
    j = Jenkins('http://jenkins.pe.local')
    jobs = j.all_jobs()
    print(jobs)
    for job, color in jobs:
        if color in ['red', 'blue', 'yellow']:
            full_info = j.job_info(job)
            last_build = j.last_build_info(job)
            when = datetime.fromtimestamp(last_build['timestamp'] / 1000)
        else:
            when = '(unknown)'
        print("{0!s:<19} {1:<6} {2}".format(when, color, job))
