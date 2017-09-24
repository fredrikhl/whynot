# encoding: utf-8
""" String reference utilities.

Usage:

>>> values = dict()
>>> references = ReferenceCollection(values)
>>> string_like = reference.format('foo is <foo>, and bar is <bar>')
>>> list(reference)
['foo', 'bar']
>>> values.update(foo='a', bar='b')
>>> str(string_like)
"'foo is a, and bar is b'"

"""
from __future__ import absolute_import, unicode_literals
import re


def unique(seq):
    """ Strip duplicates from an ordered sequence.

    >>> unique(('foo', 'bar', 'foo', 'baz', 'foo'))
    ['foo', 'bar', 'baz']
    """
    seen = set()
    # this avoids any issue with repeated lookups of `getattr(seen, 'add')` in
    # the list comprehension:
    add_seen_item = seen.add
    return [x for x in seq if not (x in seen or add_seen_item(x))]


class Reference(object):
    """ Reference to a dict item.

    Basically a __str__ implementation that fetches a string-like object from a
    dict.

    >>> source = dict(foo='a', bar='b')

    The reference is looked up in the source when __str__ is called:

    >>> Reference(source, 'foo')
    <Reference 'foo'>
    >>> str(Reference(source, 'foo'))
    'foo'

    This way we can create references to strings in source, before they are
    cretated:

    >>> Reference(source, 'baz')
    <Reference 'baz'>
    >>> str(Reference(source, 'baz'))
    Traceback (most recent call last):
    ...
    KeyError: 'baz'

    """

    def __init__(self, source, name):
        self._source = source
        self.key = name

    def __str__(self):
        return str(self._source[self.key])

    def __repr__(self):
        return "<Reference '{!s}'>".format(self.key)


class ReferenceFormat(object):
    """ Delayed formatting in a string-like object.

    This is simply a `lambda: format_string.format(*substitutions)` that can be
    passed to `str`.
    """

    def __init__(self, format_string, *substitutions):
        self.format_string = format_string
        self.substitutions = substitutions
        # Validate the format string and number of substitutions.
        # All substitutions should be str-ed, so formatting with
        # len(substitutions) of any string should work...
        format_string.format(*["test", ] * len(substitutions))

    def __str__(self):
        return self.format_string.format(*self.substitutions)

    def __repr__(self):
        return '{0}({1})'.format(
            self.__class__.__name__,
            ', '.join([repr(self.format_string), ] +
                      [repr(s) for s in self.substitutions]))


class ReferenceCollection(dict):
    """ A collection of created references.

    Basically a defaultdict that creates any reference that doesn't exist, and
    keeps track of the references that has been created.

    >>> source = dict(foo='a', bar='b')
    >>> refs = References(source)
    >>> str(refs['foo'])
    'a'
    >>> refs
    {'foo': <Reference 'foo'>}
    """

    DEFAULT_REFERENCE_PATTERN = r'[0-9a-zA-Z]+'

    def __init__(self, source):
        self._source = source

    def __missing__(self, key):
        ref = self[key] = Reference(self._source, key)
        return ref

    # TODO: how to repr?

    def format(self, raw_text, pattern=DEFAULT_REFERENCE_PATTERN):
        """ Make replacements into a format string, and build references.

        If `value` does not contain any RE_REFERENCE matches (e.g. 'hello,
        world!'), this function simply returns that string.

        >>> source = dict(foo='World!')
        >>> refs = References(source)
        >>> refs.format('Hello, World!')
        'Hello, World!'

        If `value` IS a single reference match (e.g. '<foo_bar>'), this
        function will return a Reference-object to that reference match.

        >>> refs.format('<foo>')
        <Reference foo>

        If `value` contains one or more reference matches
        (e.g.  'hello, <foo>!'), this function will return a
        RandomFormat-object.

        >>> refs.format('Hello, <foo>!')
        ReferenceFormatter('Hello, {0!s}!', <Reference 'foo'>)
        """
        # Find all references used in the text, in order
        refnames = re.findall(r'<(' + pattern + r')>', raw_text)

        if len(refnames) < 1:
            # No references, return the text unaltered.
            return raw_text

        if raw_text == "<{!s}>".format(refnames[0]):
            # Value is just a single reference, so let's return the reference.
            return self[refnames[0]]

        # Value is a mix of references (or reference and string)
        replace = unique(refnames)
        # turn all substrings '<name>' -> '{<idx>!s}'
        string_format = raw_text
        for idx, name in enumerate(replace):
            string_format = string_format.replace(
                "<{!s}>".format(name),
                "{{{:d}!s}}".format(idx))
        return ReferenceFormat(string_format,
                               *[self[name] for name in replace])
