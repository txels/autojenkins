[![Travis CI](https://travis-ci.org/txels/autojenkins.png)](https://travis-ci.org/txels/autojenkins)

autojenkins
===========

Automation (remote control) of Jenkins tasks.
Includes a class ``autojenkins.Jenkins`` that you can use to drive Jenkins.

Things you can do with it:

* Copy a job (e.g. from a template job)
* Delete a job
* Obtain the ``config.xml`` file for that job
* Trigger building of a job
* Obtain latest execution results
* ...

Sample use:

```python
from autojenkins import Jenkins

j = Jenkins('http://jenkins.pe.local')

# trigger a manual build and check results
j.build('warehouse-screens-us544_login')
j.last_result('warehouse-screens-us544_login')

# get only the result string (one of 'SUCCESS', 'UNSTABLE', 'FAILURE'):
j.last_result('warehouse-screens-us544_login')['result']

# get the configuration file for a job:
j.get_config_xml('template')

# Create a new job from a job named 'template', replacing variables
j.create_copy('my-new-job', 'template',
              repo='mbf-warehouse-screens',
              branch='us544_login',
              package='warehouse_screens')

# build
j.build('my-new-job')

# enable or disable
j.enable('my-new-job')
j.disable('my-new-job')

# check result and delete if successful:
result = j.last_result('my-new-job')['result']
if result == 'SUCCESS':
    j.delete('my-new-job')
```

Authentication
--------------

If your Jenkins server uses authentication, you can use HTTP basic
authentication in this way:

```python
jenkins = Jenkins('http://jenkins', auth=('user', 'pass'))
```

Note that you can use either a cleartext password or a Jenkins API token
as the password.
