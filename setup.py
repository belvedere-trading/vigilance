#pylint: skip-file
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

if __name__ == '__main__':
    thirdPartyPackages = open('required_packages.req').read().splitlines()
    testPackages = open('test_required_packages.req').read().splitlines()
    consoleScripts = ['vigilance = vigilance.cli:main']

    setup(name='vigilance',
          version='1.0.0',
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
