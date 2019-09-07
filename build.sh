#!/bin/sh

python3 -m pycodestyle -r **/*.py

python3 -m pylint -r n **/*.py

python3 -m nose --with-coverage --cover-package=stitcher
