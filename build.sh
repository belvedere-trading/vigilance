#!/bin/bash -xe
pylint vigilance
python setup.py coverage
doxygen 2> doxygen.err
vigilance
