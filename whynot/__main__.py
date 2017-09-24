#!/usr/bin/env python
# encoding: utf-8
""" Command line utility for `why`. """
from __future__ import absolute_import, print_function

import argparse
import os.path
import random
import sys

from . import Why
from .config import Config
from .files import get_default_path, find_config


DESCRIPTION = "Python-port of Matlab's `why.m`"
DEFAULT_CONFIG = os.path.join(get_default_path(), 'example.cfg')


def main(inargs=None):
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-c', '--config', type=str, default=DEFAULT_CONFIG)
    parser.add_argument('-n', '--seed', type=int, default=None)
    parser.add_argument('entry_point', type=str, default='default', nargs='?')

    args = parser.parse_args(inargs)

    if not args.config:
        raise ValueError("No default config available")
    if os.path.isfile(args.config):
        config = Config.from_file(args.config)
    else:
        found = find_config(args.config)
        config = Config.from_file(found)

    if args.seed is not None:
        random.seed(args.seed)

    why = Why(config)
    print(why(args.entry_point))


if __name__ == '__main__':
    main()
