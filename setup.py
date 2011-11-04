#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup


setup(
    name='autojenkins',
    description='Jenkins Remote Control Library',
    version='0.3',
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    packages=['autojenkins'],
    install_requires=['requests', 'jinja2'],
    scripts=['scripts/ajk-create'],
)
