# encoding: utf-8
""" Locate configs across multiple directories. """
from __future__ import unicode_literals, print_function

import os
import sys


# Where we'd like to install the included configs:
INSTALL_DIR = os.path.join(sys.prefix, 'share', 'whynot')

# Where the above files lives in the source repo:
SOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

ENV_DEFAULT_DIR = 'WHYNOT_DEFAULT_DIR'
ENV_PATH = 'WHYNOT_PATH'


def is_readable_dir(path):
    """ Return True if directory is readable. """
    return (bool(path) and os.path.isdir(path)
            and os.access(path, os.R_OK | os.X_OK))


def get_default_path():
    """ The default configs.

    Return the first existing, readable folder of:

      1. env[WHYNOT_DEFAULT_DIR]
      2. install_dir
      3. source_dir

    :return str,None: Default config path, if any.

    """
    for path in (os.environ.get(ENV_DEFAULT_DIR),
                 INSTALL_DIR,
                 SOURCE_DIR):
        if is_readable_dir(path):
            return path
    return None


def get_config_paths():
    """ A list of search paths that exists and are readable.

    The list is ordered so that the last item is the first that should be
    considered when looking for cheat sheets. It contains the following
    directories, if they exist and are readable:

      1. default_config()
      3. ~/.whynot/
      4. env[WHYNOT_PATH] (colon-separated list)

    :return list:
        A list of readable paths that may contain whynot configs.

    """
    return filter(
        is_readable_dir,
        list(reversed(os.environ.get(ENV_PATH, '').split(os.pathsep))) +
        [os.path.join(os.path.expanduser('~'), '.whynot'),
         get_default_path(), ])


def find_config(name, paths=None):
    """ A mapping of config shortname to names to filename. """
    if not paths:
        paths = get_config_paths()

    for path in paths:
        for filename in os.listdir(path):
            base, ext = os.path.splitext(filename)
            if ext == '.cfg' and base == name:
                return os.path.join(path, filename)
    return None
