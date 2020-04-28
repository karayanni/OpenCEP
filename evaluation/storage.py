"""
lower bound and the upper bound
"""
from abc import abstractmethod
from collections.abc import MutableSequence
from itertools import chain
import bisect
from misc.Utils import find_partial_match_by_timestamp, find_partial_match_by_condition
from datetime import datetime
from typing import List
from evaluation.PartialMatch import PartialMatch

# from blist import blist B+ tree like list
# Note: for mutable collections like ours we shouldn't return self but a copy of self.
# if we were immutable we could return self because the user aslan can't use our collection


class Storage(MutableSequence):
    """
    This stores all the partial matches
    """

    # TODO def get_parial_matches(self, pm):
    @abstractmethod
    def __init__(self):
        self._container: MutableSequence
        self._key: callable
        self.sort_by_timestamp: bool

    def append(self, pm):
        self._container.append(pm)

    def get_sorting_key(self):
        return self._key

    def insert(self, index, item):  # abstract in MutableSequence      for x.insert(i,a)
        self._container.insert(index, item)

    def __setitem__(self, index, item):  # abstract in MutableSequence      for x[i] = a
        self._container[index] = item

    def __getitem__(self, index):  # abstract in MutableSequence      for y = x[i]
        """return self._container[index] => not very good.
        * index can be a slice [:] which makes us return a list when we should return an SortedStorage object
        """
        result = self._container[index]
        return SortedStorage(result, self._key) if isinstance(index, slice) else result

    def __len__(self):  # abstract in MutableSequence      for len(x)
        return len(self._container)

    def __delitem__(self, index):  # abstract in MutableSequence      for del x[i]
        del self._container[index]

    def __contains__(self, item):
        return item in self._container  # todo : we can use bisect here instead

    def __iter__(self):
        return iter(self._container)

    def __add__(self, rhs):  #      for s1 + s2
        pass

    # TODO: we can implement the index method(overriding it actually) and other methods with BINARY SEARCH.
    """def index(self, item):
           index = bisect_left(self._container, item)
           if (index != len(self._container)) and (self._container[index] == item):
                return index
            raise ValueError("{} not found".format(repr(item)))
        if we implement this function then we can let __contains__ call it to to be O(logn)
    """

    # FOR TESTS
    def __repr__(self):
        return "Storage contains {}".format(
            repr(self._container) if self._container else "Nothing"
        )

    def __eq__(self, rhs):
        if not isinstance(rhs, Storage):
            return NotImplemented
        return self._container == rhs._container

    def __ne__(self, rhs):
        if not isinstance(rhs, Storage):
            return NotImplemented
        return self._container != rhs._container


class SortedStorage(Storage):
    def __init__(self, key=None, sort_by_timestamp=False, array=[]):
        self._container = array
        self._key = key
        self.sort_by_timestamp = sort_by_timestamp
        self._relation_op = None

    def add(self, pm):
        index = find_partial_match_by_condition(
            self._container, self._key(pm), self._key
        )
        self._container.insert(index, pm)

    def get(self, value):
        pass

    # this also can return many values
    def _get_equal(self, value):
        pass

    def _get_unequal(self, value):
        pass

    def _get_greater_or_equal(self, value):
        pass

    def _get_smaller_or_equal(self, value):
        pass

    def _get_greater(self, value):
        # returns all pms that have smaller timestamp than the given timestamp
        index = find_partial_match_by_condition(self._container, value, self._key)
        return SortedStorage(self._container[index:], self._key)

    def _get_smaller(self, value):
        # returns all pms that have smaller timestamp than the given timestamp
        index = find_partial_match_by_condition(self._container, value, self._key)
        # TODO create it with the appropriate key maybe
        return SortedStorage(self._container[:index], self._key)

    # implementing add or extend depends on whether we want a new object or update the current SortedStorage.
    # if we need something we'd need extend with O(1)
    def __add__(self, rhs):  #      for s1 + s2
        return SortedStorage(list(chain(self._container, rhs._container)), self._key)

    def get_partial_matches(self, value, side_of_equation: str, relational_op="="):
        if side_of_equation == "right":
            if relational_op == ">":
                pass

        return None


class UnsortedStorage(Storage):
    def __init__(self, array):
        self._container = array

    def get(self):
        return UnsortedStorage(self._container)

    # the same as def append()
    def add(self, pm):
        self._container.append(pm)


"""class BListStorage(Storage):
    def __init__(self):
        self._container = []"""


# https://books.google.co.il/books?id=jnEoBgAAQBAJ&pg=A119&lpg=PA119&dq=difference+between+__setitem__+and+insert+in+python&source=bl&ots=5WjkK7Acbl&sig=ACfU3U06CgfJju4aTo8K20rhq0tIul6oBg&hl=en&sa=X&ved=2ahUKEwjo9oGLpuHoAhVTXMAKHf5jA68Q6AEwDnoECA0QOw#v=onepage&q=difference%20between%20__setitem__%20and%20insert%20in%20python&f=false
