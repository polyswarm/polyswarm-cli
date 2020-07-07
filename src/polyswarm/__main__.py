#!/usr/bin/env python3
from __future__ import absolute_import
import os
import sys
from polyswarm.client.polyswarm import polyswarm_cli


def main():
    # fixing the name of the entrypoint when the module is executed as
    # python -m polyswarm
    # https://docs.python.org/3/library/__main__.html
    entrypoint_name = os.path.basename(sys.argv[0])
    if entrypoint_name == '__main__.py':
        entrypoint_name = 'polyswarm'

    polyswarm_cli(prog_name=entrypoint_name, obj={})


if __name__ == '__main__':
    main()
