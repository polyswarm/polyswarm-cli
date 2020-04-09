
# Polyswarm Customer CLI

A CLI tool for interacting with the PolySwarm Customer APIs.

Supports Python 2.7 and greater.

## Installation

From PyPI:

    pip install polyswarm

From source:

    python setup.py install

If you want yara validation (optional):

    pip install -e .[yara]

> If you get an error about a missing package named `wheel`, that means your version of pip or setuptools is too old.
> You need pip >= 19.0 and setuptools >= 40.8.0. 
> To update pip, run `pip install -U pip`.
> To update setuptools, run `pip install -U setuptools`

## Usage


See the [Polyswarm Customer CLI documentation](https://docs.polyswarm.io/docs/polyswarm-customer-cli) for usage guidance.

## Automated Tests

To run automated tests suite (unit and integration):

    pip install -r requirements.txt
    pytest

To check current coverage by tests:

    pytest --cov=polyswarm tests/

## Questions? Problems?

File a ticket or email us at `info@polyswarm.io`.
