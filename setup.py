#!/usr/bin/env python

from setuptools import setup

setup(name='Simple Share',
      version='0.0.1',
      description='Simple file sharing service',
      author='A. Bondis',
      author_email='abondis@kerunix.com',
      packages=['simpleshare'],
      install_requires=[
          'bottle',
          'beaker',
          'bottle-cork'],
)
