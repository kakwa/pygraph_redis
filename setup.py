#!/usr/bin/env python
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
import os
import sys
from setuptools import setup

from distutils.core import setup

try:
    f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
    description = f.read()
    f.close()
except IOError:
    description = 'pygraph_redis'

try:
    license = open('LICENSE').read()
except IOError:
    license = 'MIT'

try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand

    class PyTest(TestCommand):
        def finalize_options(self):
            TestCommand.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            #import here, cause outside the eggs aren't loaded
            import pytest
            errno = pytest.main(self.test_args)
            sys.exit(errno)

except ImportError:

    from distutils.core import setup
    PyTest = lambda x: x

setup(
        name='pygraph_redis',
        version='0.2.1',
        description='Python Library to manipulate directed graphs in redis',
        long_description = description,
        author='Pierre-Francois Carpentier',
        author_email='carpentier.pf@gmail.com',
        license=license,
        url='https://github.com/kakwa/pygraph_redis',
        tests_require=['pytest'],
        cmdclass={'test': PyTest},
        install_requires=[
            "setuptools",
            "redis",
            ],
        packages = ['pygraph_redis',],
        package_dir = {'': 'src'},
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3']
)
