#!/bin/sh
pylint vigilence
python setup.py coverage
vigilence coverage.xml --type cobertura
doxygen 2> doxygen.err
vigilence doxygen.err --type doxygen --config vigilence_doc.yaml
