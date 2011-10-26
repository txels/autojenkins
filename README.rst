autojenkins
===========

Automation (remote control) of Jenkins tasks.

Includes a ``autojenkins.Jenkins`` class that you can use to drive Jenkins.

Things you can do with it:

* Copy a job (e.g. from a template job)

* Delete a job

* Obtain the ``config.xml`` file for that job

* Trigger building of a job

* Obtain latest execution results

* ...

Sample use:

    from autojenkins import Jenkins
    j = Jenkins('http://jenkins.pe.local')
    j.build('warehouse-screens-us544_login')
    j.last_result('warehouse-screens-us544_login')


TODO
----

* Create a job from scratch (e.g. create the ``config.xml`` from a Jinja2
  template and some parameters, and post it to Jenkins)
