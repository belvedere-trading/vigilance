#pylint: skip-file
from __future__ import print_function
import re
import six
import subprocess
import sys
from distutils.cmd import Command
from setuptools import setup, find_packages

def run_with_exit(command):
    returnCode = subprocess.call(command)
    if returnCode:
        sys.exit(returnCode)

class TestWithCoverage(Command):
    """Runs unit tests along with a test coverage report.
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        run_with_exit(['coverage', 'run', 'setup.py', 'nosetests'])
        run_with_exit(['coverage', 'report', '-m'])
        run_with_exit(['coverage', 'xml'])

tag_regex = re.compile(r'v\d\.\d\.\d')
def get_tagged_version():
    process = subprocess.Popen(['git', 'describe', '--abbrev=0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = six.ensure_text(out)
    if process.returncode:
        print('Failed to get tagged version: {}'.format(err))
        sys.exit(process.returncode)
    out = out.strip()
    if not re.match(tag_regex, out):
        print('Found invalid tag: {}'.format(out))
        sys.exit(-1)
    return out[1:]

if __name__ == '__main__':
    thirdPartyPackages = open('required_packages.req').read().splitlines()
    testPackages = open('test_required_packages.req').read().splitlines()
    consoleScripts = ['vigilance = vigilance.cli:main']

    setup(name='vigilance',
          version=get_tagged_version(),
          author='Belvedere Trading',
          author_email='jkaye@belvederetrading.com',
          packages=find_packages(),
          url='http://pypi:28080/simple/Vigilance/',
          description='A utility for enforcing minimum code coverage',
          install_requires=thirdPartyPackages,
          tests_require=testPackages,
          test_loader='nose.loader:TestLoader',
          test_suite='vigilance',
          entry_points={
              'console_scripts': consoleScripts
          },
          scripts=['doxypy_filter'],
          cmdclass={'coverage': TestWithCoverage})
