#!/bin/bash

BRANCH=`git rev-parse --abbrev-ref HEAD`
pushd /tmp

git clone https://github.com/polyswarm/polyswarm-api

cd polyswarm-api

# ignore if fails
git checkout $BRANCH || true

pip install .

popd

pip install .

polyswarm -h

pytest -s -v
