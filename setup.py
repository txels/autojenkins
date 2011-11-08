#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup
long_description = open('README.rst').read()

setup(
    name='autojenkins',
    description='Jenkins Remote Control Library',
    #long_description=long_description,
    version='0.4.1',
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    url='https://github.com/txels/autojenkins',
    packages=['autojenkins'],
    install_requires=['requests', 'jinja2'],
    scripts=['scripts/ajk-create'],
)
