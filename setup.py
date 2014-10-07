#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

from ajk_version import __version__


setup(
    name='autojenkins',
    description='Jenkins Remote Control Library',
    long_description=open('README.rst').read(),
    version=__version__,
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    url='https://github.com/txels/autojenkins',
    packages=['autojenkins'],
    install_requires=['docopt', 'requests', 'jinja2'],
    entry_points=dict(
        console_scripts=[
            'autojenkins = autojenkins.run:Commands.main'
        ],
    ),
    #include_package_data=True,
    package_data={
        '': ['*.txt', '*.rst'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
    ],
)
