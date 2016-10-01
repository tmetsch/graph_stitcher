#!/bin/sh

pep8 -r **/*.py

pylint -r n **/*.py

nosetests --with-coverage --cover-package=stitcher
