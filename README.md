
# Polyswarm Customer CLI

A CLI tool for interacting with the PolySwarm Customer APIs.

Supports Python 3.7 and greater.

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

### Command line client
See the [Polyswarm Customer CLI documentation](https://docs.polyswarm.io/consumers/polyswarm-customer-cli-v2) for usage guidance.

### Using as a package

The `polyswarm-cli` package is built on top of the `polyswarm-api` package, and it includes
a set of higher-level methods that facilitates the usage of parallelism when making requests 
to the api. We provide a class `Polyswarm` that extends from `PolyswarmAPI` and includes 
these methods. For example:

```python
from polyswarm.polyswarm import Polyswarm
api = Polyswarm('my-api-key')
results = api.search_hashes(['e182cdfd5e7463d11f5e7bc49b4377ab25e58b9ff04266df3c34e6261c7b0df9',
                             'd80a1e42791d17cbce8d053afccd1dae7fb9f615676cb81a3a1699e86c344cb8',
                             '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
for result in results:
    print(result.id)
```

Each hash lookup is done in a different thread using a `ThreadPoolExecutor` and results are yielded
as they come in in the same order as in the input. All functionality that is available in the command
line tool is also available for developers through this class.

## Automated Tests

To run automated tests suite (unit and integration):

    pip install -r requirements.txt
    pytest

To check current coverage by tests:

    pytest --cov=polyswarm tests/

## Questions? Problems?

File a ticket or email us at `info@polyswarm.io`.
