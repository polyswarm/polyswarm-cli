#!/bin/bash

BRANCH=`git rev-parse --abbrev-ref HEAD`
pushd /tmp

git clone https://github.com/polyswarm/polyswarm-api

cd polyswarm-api

# ignore if fails
git checkout $BRANCH || true

pip install .

popd

if ! pip install . ; then
    exit 1
fi


if ! polyswarm -h; then
    exit 2
fi

pytest -s -v
