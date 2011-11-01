from autojenkins import Jenkins


if __name__ == '__main__':
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
