# encoding: utf-8
""" Config utils for parsing a config into a collection of RandomStrings.

Format
------
Each section is a collection of int and string pairs.

    [<section_name>]
    <int>: <str>
    # <comment>


Example config
--------------

An example config:

    [greeting]
    3: hello
    1: goodbye

    [object]
    1: world
    1: sir

    [action]
    9: <greeting>
    1: fuck off

    [result]
    1: <greeting>, <object>!

"""
from __future__ import absolute_import, unicode_literals
import re
from collections import OrderedDict
from pyparsing import Suppress, Word, Regex, nums
from .refs import ReferenceCollection
from .weight import RandomString

#
# config syntax items
#
COMMENT = "comment"
SECTION = "section"
WEIGHT = "weight"
VALUE = "value"


#
# parser syntax
#

# Valid section names
RE_SECTION_NAME = re.compile(r'[-_a-zA-Z0-9]+')

# >>> SECTION_LINE.parseString("[foo]")
# (['foo'], {'section': ['foo']})
SECTION_LINE = (
    Suppress("[") +
    Regex(RE_SECTION_NAME.pattern)(SECTION) +
    Suppress("]"))

# >>> COMMENT_LINE.parseString("# a comment")
# (['a comment'], {u'comment': ['a comment']})
COMMENT_LINE = (
    Suppress("#") +
    Regex(r".*$")(COMMENT))

# >>> VALUE_LINE.parseString("42: foo")
# ([42, 'foo'], {'value': ['foo'], 'weight': [42]})
VALUE_LINE = (
    Word(nums)(WEIGHT).setParseAction(lambda t: int(t[0])) +
    Suppress(":") +
    Regex(r".+")(VALUE))

CONFIG_LINE = COMMENT_LINE ^ SECTION_LINE ^ VALUE_LINE


class ConfigException(Exception):
    """ A simple exception for the config file parser. """

    def __init__(self, lineno, line, exc):
        self.lineno = lineno
        self.line = line
        self.cause = exc
        super(ConfigException, self).__init__(
            "line {:d}: '{!s}' ({!s} - {!s})".format(
                lineno, line, exc.__class__.__name__, str(exc)))


def parse_config(text):
    """ Generator that iterates through a config string.

    Iterates through lines of text, and yields a tuple for each line with:

    - The line number (int)
    - The line content (str)
    - The parse results for that line (None if the line is empty).

    """
    for lineno, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            yield lineno, line, None
            continue
        try:
            data = CONFIG_LINE.parseString(line)
        except Exception as e:
            # TODO: Raise with traceback
            raise ConfigException(lineno, line, e)
        yield lineno, line, data


class Config(OrderedDict):
    """ A collection of named RandomString items. """

    @property
    def references(self):
        """ References used in contained collections. """
        try:
            self.__refs
        except AttributeError:
            self.__refs = ReferenceCollection(self)
        return self.__refs

    def __missing__(self, section_name):
        if section_name is None:
            raise ValueError("Invalid section name")
        section = self[section_name] = RandomString()
        return section

    @classmethod
    def from_string(cls, config_string):
        config = cls()

        def check_section(conf, name):
            """ Check if section is empty. """
            if name is not None and len(conf[name]) < 1:
                raise ValueError(
                    "Empty collection '{!s}'".format(name))

        current_section = None
        for lineno, line, result in parse_config(config_string):
            try:
                if result is None:
                    # Empty line clears current section
                    check_section(config, current_section)
                    current_section = None
                elif COMMENT in result:
                    # Line is a comment
                    pass
                elif SECTION in result:
                    # Line is a new section
                    check_section(config, current_section)
                    current_section = result[SECTION]
                elif all(n in result for n in (VALUE, WEIGHT)):
                    # Line is a weighted text item within the previous section
                    if current_section is None:
                        raise ValueError("Item outside section")
                    text = config.references.format(
                        result[VALUE],
                        pattern=RE_SECTION_NAME.pattern)
                    weight = result[WEIGHT]
                    config[current_section].add(text, weight=weight)
                else:
                    raise ValueError("Invalid line")
            except Exception as e:
                raise ConfigException(lineno, line, e)

        for ref in config.references:
            if ref not in config:
                raise ValueError(
                    "Reference to missing collection '{!s}'".format(ref))

        return config

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'Ur') as config_file:
            return cls.from_string(config_file.read())


def main(inargs=None):
    """ python -m why.config [filename]

    Dumps the parsed config
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args(inargs)

    collections = Config.from_file(args.filename)
    for collection in collections:
        print '[{!s}]'.format(collection)
        for item in collections[collection].items:
            print '{i.weight!s}: {i.value!r}'.format(i=item)
        print ''


if __name__ == '__main__':
    main()
