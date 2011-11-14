#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup
long_description = open('README.rst').read()

setup(
    name='autojenkins',
    description='Jenkins Remote Control Library',
    long_description=long_description,
    version='0.4.2',
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    url='https://github.com/txels/autojenkins',
    packages=['autojenkins'],
    install_requires=['requests', 'jinja2'],
    scripts=['scripts/ajk-create', 'scripts/ajk-delete'],
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

