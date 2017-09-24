# encoding: utf-8
""" Python-port of matlab's `why`. """
from __future__ import absolute_import

DEFAULT_SOURCE = "default"


class Why(object):
    """ Get a random reason for the question `why?`. """

    def __init__(self, config):
        self.data = config

    def __call__(self, source=DEFAULT_SOURCE):
        reason = str(self.data[source])
        # Capitalize without making anything lowercase:
        return reason[0].upper() + reason[1:]
