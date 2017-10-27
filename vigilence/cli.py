"""@ingroup vigilence
@file
Contains the console API for Vigilence.
"""
import click

from vigilence.suite import QualitySuite

@click.command(short_help='Verify code coverage metrics against a set of constraints')
@click.argument('quality-report', type=click.File())
@click.option('--type', 'coverage_type', type=click.Choice(QualitySuite.available_suites()), default='cobertura')
@click.option('--config', type=click.File(), default='vigilence.yaml')
def main(quality_report, coverage_type, config): #pylint: disable=missing-docstring, invalid-name
    suite = QualitySuite.get_suite(coverage_type)
    suite.run(config.read(), quality_report.read())
