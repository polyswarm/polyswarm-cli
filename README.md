
# Polyswarm Customer CLI

A CLI tool for interacting with the PolySwarm Customer APIs.

Supports Python 2.7 and greater.

## Installation

From PyPI:

    pip install polyswarm

From source:

    python setup.py install
    
With Docker:

    docker build -t polyswarm/cli -f docker/Dockerfile .

## Usage


See the [Polyswarm Customer CLI documentation](https://docs.polyswarm.io/docs/polyswarm-customer-cli) for usage guidance.

## Running with Docker

Scan a folder of malware samples. Example has samples in directory `/home/user/malware`

    docker run -e POLYSWARM_API_KEY=<api key here> -v /home/user/malware:malware polyswarm/cli scan /malware


## Questions? Problems?

File a ticket or email us at `info@polyswarm.io`.
