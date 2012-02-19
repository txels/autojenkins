#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup
long_description = open('README.rst').read()

setup(
    name='autojenkins',
    description='Jenkins Remote Control Library',
    long_description=long_description,
    version='0.5.1',
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    url='https://github.com/txels/autojenkins',
    packages=['autojenkins'],
    install_requires=['requests', 'jinja2'],
    entry_points = dict(
        console_scripts = [
            'ajk-create = autojenkins.run:Commands.create',
            'ajk-delete = autojenkins.run:Commands.delete',
            'ajk-list = autojenkins.run:Commands.list',
        ],
    ),
    #include_package_data=True,
    package_data = {
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

