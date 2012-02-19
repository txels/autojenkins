#!/bin/bash

PROJECT="autojenkins"

#remove .pyc files
find ./${PROJECT} -name "*.pyc" -exec rm {} \;

# Run tests with coverage
nosetests --with-xunit --cover-erase --with-xcoverage --cover-inclusive --cover-html --cover-package=${PROJECT}


# Build documentation
( cd docs; make clean html SPHINXOPTS="-a -n -w sphinx-output" )

# PEP8
pep8 --ignore=W293 -r ${PROJECT} > pep8.txt || echo "PEP-8 violations."


