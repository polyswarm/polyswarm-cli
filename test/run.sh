#!/bin/bash

BRANCH=`git rev-parse --abbrev-ref HEAD`
pushd /tmp

git clone https://github.com/polyswarm/polyswarm-api

cd polyswarm-api

# ignore if fails
if git checkout $BRANCH ; then
    echo "checked out $BRANCH"
else
    echo "couldn't find $BRANCH, using master"
fi

pip install .

popd

if ! pip install . ; then
    exit 1
fi


if ! polyswarm -h; then
    exit 2
fi

pytest -s -v
