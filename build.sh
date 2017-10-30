#!/bin/bash -xe
pylint vigilence
python setup.py coverage
doxygen 2> doxygen.err
vigilence
