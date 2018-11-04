#!/bin/sh

pycodestyle -r **/*.py

pylint -r n **/*.py

nosetests --with-coverage --cover-package=stitcher
