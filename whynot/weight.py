# encoding: utf-8
""" Randomized, weighted collections. """
from __future__ import absolute_import, unicode_literals
import random


class WeightedItem(object):
    """ An object that bundles weight and value. """

    def __init__(self, value, weight=1):
        self.weight = weight
        self.value = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = int(value)

    def __repr__(self):
        return ('{0.__class__.__name__}'
                '(0.value!r},'
                ' weight={0.weight!r})').format(self)


class WeightedCollection(object):
    """ A collection of (weighted) items to pick from.  """

    def __init__(self, *items):
        self.items = list()
        for item in items:
            if not isinstance(item, WeightedItem):
                raise TypeError("Not a WeightedItem")
            self.items.append(item)

    def add(self, value, weight=1):
        # TODO: Increase weight if value already exists in self?
        self.items.append(WeightedItem(value, weight=weight))

    def __len__(self):
        return sum(i.weight for i in self.items)

    def __iter__(self):
        """ Iterator that expands (multiplies) weighted items. """
        for item in self.items:
            for _ in range(item.weight):
                yield item

    def __getitem__(self, n):
        return list(self)[n % len(self)].value

    def __repr__(self):
        if getattr(self, '_run_repr', False):
            self._run_repr = False
            return 'recursive...'
        else:
            self._run_repr = True
        value = '{!s}({!s})'.format(
            self.__class__.__name__,
            ', '.join(repr(s) for s in self.items))
        self._run_repr = False
        return value


class RandomString(WeightedCollection):
    """ Delayed string presentation of a `WeightedCollection` item. """

    def __str__(self):
        """ A random string value from this collection. """
        item = random.choice(list(self)).value
        if callable(item):
            return str(item())
        else:
            return str(item)
