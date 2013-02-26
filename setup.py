#!/usr/bin/env python
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
from setuptools import setup

from distutils.core import setup

setup(name='pygraph_redis',
      version='0.0.1',
      description='Python Library to manipulate graph in redis',
      author='Pierre-Francois Carpentier',
      author_email='carpentier.pf@gmail.com',
      license='MIT',
      url='',
      install_requires=[
          "setuptools",
          "redis",
          ],
      packages = ['pygraph_redis',],
      package_dir = {'': 'src'},
      namespace_packages = ['pygraph_redis', ],
     )
