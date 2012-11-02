Introduction to AutoJenkins
===========================

AutoJenkins was written to handle automation (remote control) of Jenkins tasks.
Includes a class ``autojenkins.Jenkins`` that you can use to drive Jenkins.

Things you can do with it:

* Copy a job (e.g. from a template job)
* Delete a job
* Obtain the ``config.xml`` file for that job
* Trigger building of a job
* Obtain latest execution results
* ...

AutoJenkins may be used as an API or as a command-line tool.

AutoJenkins as API
------------------

Sample use:

.. code-block:: python

    from autojenkins import Jenkins

    j = Jenkins('http://jenkins.pe.local')
    #You can now add verify_ssl_cert=False argument to the instantiation
    #so that all requests will ignore SSL certificate errros, should you need that 
    #i.e. j = Jenkins('https://my.secure.jenkins', verify_ssl_cert=False)

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

    # check result and delete if successful:
    result = j.last_result('my-new-job')['result']
    if result == 'SUCCESS':
        j.delete('my-new-job')

AutoJenkins from the Command Line
---------------------------------

Available commands:

* ``ajk-list`` - list all jobs in a server
* ``ajk-create`` - create a job
* ``ajk-build`` - start building a job
* ``ajk-delete`` - delete a job

``ajk-list``
~~~~~~~~~~~~

List all jobs in a Jenkins server. Each line in the output represents
a job, and is colored according to the job's last build state:

* Blue: success
* Yellow: unstable
* Red: failure
* Gray: not built

A ``*`` symbol next to a job name indicates that the job is being built
right now.

If instead of colored output, you prefer a string stating the status
of the build, use the ``--no-color`` option. This is useful if you
e.g. want to pipe the output into a ``grep`` command that filters
jobs depending on status.

.. code-block:: none

    $ ajk-list -h

    Usage: ajk-list host

    Run autojenkins to list all jobs.

    Options:
      -h, --help      show this help message and exit
      -u USER, --user=USER
                      username
      -p PASSWORD, --password=PASSWORD
                      password or token
      -n, --no-color  do not use colored output
      -r, --raw       only output job names, so that output is more usable for
                      piping to other processes

``ajk-create``
~~~~~~~~~~~~~~

Create a job from a template job, replacing variables that
use the django/jinja2 syntax ``{{ variable }}``.

Usage help:

.. code-block:: none

    $ ajk-create -h

    Usage: ajk-create host [jobname] [options]

    Run autojenkins to create a job.

    Options:
      -h, --help            show this help message and exit
      -u USER, --user=USER  username
      -p PASSWORD, --password=PASSWORD
                            password or token
      -D VAR=VALUE          substitution variables to be used in the template
      -t TEMPLATE, --template=TEMPLATE
                            the template job to copy from
      -b, --build           start a build right after creation

Sample command:

.. code-block:: none

    $ ajk-create http://my.server my-job -t template -Dbranch=my-branch

``ajk-build``
~~~~~~~~~~~~~

Trigger the building of a job, optionally waiting for it to complete.

When used with the ``--wait`` flag, it will exit with a status different than
0 if the build is not successful. This makes it useful when including this in
shell scripts that depend on a successful build to take further action.

Usage help:

.. code-block:: none

    $ ajk-build -h

    Usage: ajk-build host [jobname] [options]

    Run autojenkins to build a job.

    Options:
      -h, --help             show this help message and exit
      -u USER, --user=USER   username
      -p PASSWORD, --password=PASSWORD
                             password or token
      -w, --wait             wait until the build completes

``ajk-delete``
~~~~~~~~~~~~~~

Delete a job from a Jenkins server.

Usage help:

.. code-block:: none

    $ ajk-delete -h

    Usage: ajk-delete host [jobname]... [options]

    Run autojenkins to delete one or more jobs.

    Options:
      -h, --help             show this help message and exit
      -u USER, --user=USER   username
      -p PASSWORD, --password=PASSWORD
                             password or token


More Info
---------

Sources can be found in Github at https://github.com/txels/autojenkins
