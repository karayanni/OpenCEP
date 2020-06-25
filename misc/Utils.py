"""
This file contains various useful functions utilized by different project modules.
"""

from datetime import datetime
from typing import List

from base.Pattern import Pattern
from base.PatternStructure import QItem
from itertools import combinations
from base.PatternStructure import SeqOperator
from base.PatternMatch import PatternMatch
from copy import deepcopy

from evaluation.PartialMatch import PartialMatch
from misc.IOUtils import Stream


def find_partial_match_by_timestamp(partial_matches: List[PartialMatch], timestamp: datetime):
    """
    Returns the partial match from the given list such that its timestamp is the closest to the given timestamp.
    The list is assumed to be sorted according to the earliest event timestamp.
    """
    # should count how many PMs are before last date.
    length = len(partial_matches)
    if length == 0 or partial_matches[0].first_timestamp >= timestamp:
        return 0
    if length == 1:  # here we already know that first item's date < lastDate
        return 1
    if partial_matches[-1].first_timestamp < timestamp:
        return length

    start = 0
    end = length - 1
    while start <= end:
        mid = (start + end) // 2
        mid_date = partial_matches[mid].first_timestamp
        if partial_matches[mid - 1].first_timestamp < timestamp <= mid_date:
            return mid
        elif timestamp > mid_date:
            start = mid + 1
        else:
            end = mid - 1

    # shouldn't get here, because we know not all partial matches are up to date (nor expired),
    # which means an index should be found.
    raise Exception()


def is_float(x: str):
    try:
        _ = float(x)
    except ValueError:
        return False
    else:
        return True


def is_int(x: str):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def str_to_number(x: str):
    if is_int(x):
        return int(x)
    elif is_float(x):
        return float(x)
    else:
        return x


def get_order_by_occurrences(qitems: List[QItem], occurrences: dict):
    """
    Sorts the given list according to the occurrences dictionary.
    """
    temp_list = [(i, occurrences[qitems[i].event_type]) for i in range(len(qitems))]
    temp_list = sorted(temp_list, key=lambda x: x[1])
    return [i[0] for i in temp_list]


def get_all_disjoint_sets(s: frozenset):
    """
    A generator for all disjoint splits of a set.
    """
    if len(s) == 2:
        yield (frozenset({t}) for t in s)
        return

    first = next(iter(s))
    for i in range(len(s) - 1):
        for c in combinations(s.difference({first}), i):
            set1 = frozenset(c).union({first})
            set2 = s.difference(set1)
            yield set1, set2


def merge(arr1: list, arr2: list, key=lambda x: x):
    """
    Merges two lists. The comparison is performed according to the given key function.
    """
    new_len = len(arr1) + len(arr2)
    ret = []
    i = i1 = i2 = 0
    while i < new_len and i1 < len(arr1) and i2 < len(arr2):
        if key(arr1[i1]) < key(arr2[i2]):
            ret.append(arr1[i1])
            i1 += 1
        else:
            ret.append(arr2[i2])
            i2 += 1
        i += 1

    while i1 < len(arr1):
        ret.append(arr1[i1])
        i1 += 1

    while i2 < len(arr2):
        ret.append(arr2[i2])
        i2 += 1

    return ret


def merge_according_to(arr1: list, arr2: list, actual1: list, actual2: list, key: callable = lambda x: x):
    """
    Merge arrays actual1, actual2 according to the way a merge would be done on arr1 and arr2.
    Used in a partial match merge function - the reorders are given, and the partial matches is merged
    according to the reorders.
    """
    if len(arr1) != len(actual1) or len(arr2) != len(actual2):
        raise Exception()

    new_len = len(arr1) + len(arr2)
    ret = []
    i = i1 = i2 = 0
    while i < new_len and i1 < len(arr1) and i2 < len(arr2):
        if key(arr1[i1]) < key(arr2[i2]):
            ret.append(actual1[i1])
            i1 += 1
        else:
            ret.append(actual2[i2])
            i2 += 1
        i += 1

    while i1 < len(arr1):
        ret.append(actual1[i1])
        i1 += 1

    while i2 < len(arr2):
        ret.append(actual2[i2])
        i2 += 1

    return ret


def is_sorted(arr: list, key: callable = lambda x: x):
    """
    Returns True if the given list is sorted with respect to the given comparator function and False otherwise.
    """
    if len(arr) == 0:
        return True

    for i in range(len(arr) - 1):
        if key(arr[i]) > key(arr[i + 1]):
            return False

    return True


def generate_matches(pattern: Pattern, stream: Stream):
    """
    A recursive, very inefficient pattern match finder.
    It is used as our test creator.
    """
    args = pattern.structure.args
    types = {qitem.eventType for qitem in args}
    is_seq = (pattern.structure.get_top_operator() == SeqOperator)
    events = {}
    matches = []
    for event in stream:
        if event.eventType in types:
            if event.eventType in events.keys():
                events[event.eventType].append(event)
            else:
                events[event.eventType] = [event]
    generate_matches_recursive(pattern, events, is_seq, [], datetime.max, datetime.min, matches, {})
    return matches


def generate_matches_recursive(pattern: Pattern, events: dict, is_seq: bool, match: list, min_event_timestamp: datetime,
                               max_event_timestamp: datetime,
                               matches: list, binding: dict, loop: int = 0):
    pattern_length = len(pattern.structure.args)
    if loop == pattern_length:
        if pattern.condition.eval(binding):
            if not does_match_exist(matches, match):
                matches.append(PatternMatch(deepcopy(match)))
    else:
        qitem = pattern.structure.args[loop]
        for event in events[qitem.eventType]:
            min_date = min(min_event_timestamp, event.date)
            max_date = max(max_event_timestamp, event.date)
            binding[qitem.name] = event.event
            if max_date - min_date <= pattern.window:
                if not is_seq or len(match) == 0 or match[-1].date <= event.date:
                    match.append(event)
                    generate_matches_recursive(pattern, events, is_seq, match, min_date, max_date, matches, binding,
                                               loop + 1)
                    del match[-1]
        del binding[qitem.name]


def does_match_exist(matches: list, match: list):
    """
    Returns True if the given match exists in the list of matches and False otherwise.
    """
    for match2 in matches:
        if len(match) == len(match2.events):
            is_equal = True
            for i in range(len(match)):
                if match[i] != match2.events[i]:
                    is_equal = False
                    break
            if is_equal:
                return True
    return False


def get_first_index(container, to_find_value, key: callable):
    start = 0
    end = len(container) - 1

    while start < end:
        mid = (start + end) // 2
        mid_value = key(container[mid])

        if mid_value < to_find_value < key(container[mid + 1]):
            return mid
        if mid_value >= to_find_value:
            end = mid
        else:
            start = mid + 1

    if start == end:
        mid_value = key(container[start])
        if mid_value > to_find_value:
            return start - 1
        elif mid_value < to_find_value:
            return start + 1
        else:
            return start

    return 0


def get_last_index(container, to_find_value, key):
    start = 0
    end = len(container) - 1

    while start < end:
        mid = (start + end) // 2
        mid_value = key(container[mid])

        if mid_value < to_find_value < key(container[mid + 1]):
            return mid + 1
        if mid_value <= to_find_value:
            start = mid + 1
        else:
            end = mid

    if start == end:
        mid_value = key(container[start])
        if mid_value > to_find_value:
            return start - 1
        elif mid_value < to_find_value:
            return start + 1
        else:
            return start

    return 0
