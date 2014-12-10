#!/usr/bin/env python

# How to build source distribution
# python setup.py sdist --format bztar
# python setup.py sdist --format gztar
# python setup.py sdist --format zip

import os
from setuptools import setup

from fgzip import __version__

setup(name="fgzip",
      version=__version__,
      description="Fast GZIP module for Python 2.x and 3.x",
      author="Marc-Andre Legault",
      author_email="legaultmarc@gmail.com",
      url="https://github.com/legaultmarc",
      license="CC BY-NC 4.0",
      py_modules=["fgzip"],
      classifiers=['Operating System :: Linux',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4'])

