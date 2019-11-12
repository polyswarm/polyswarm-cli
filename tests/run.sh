#!/bin/bash

pushd /tmp

git clone https://github.com/polyswarm/polyswarm-api

cd polyswarm-api

# ignore if fails
if git checkout $CI_COMMIT_REF_NAME ; then
    echo "checked out $CI_COMMIT_REF_NAME"
else
    echo "couldn't find $CI_COMMIT_REF_NAME, using master"
fi

pip install .

popd

if ! pip install -e . ; then
    exit 1
fi


if ! polyswarm -h; then
    exit 2
fi

pytest -s -v