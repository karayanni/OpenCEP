from abc import ABC
from queue import Queue
from datetime import timedelta, datetime
from base.Formula import TrueFormula, Formula
from evaluation.PartialMatch import PartialMatch
from misc.Utils import find_partial_match_by_timestamp
from evaluation.Storage import Storage
from evaluation.Storage import TreeStorageParameters


class Node(ABC):
    """
    This class represents a single node of an evaluation tree.
    """
    def __init__(self, sliding_window: timedelta, parent):
        self._parent = parent
        self._sliding_window = sliding_window
        self._partial_matches: Storage[PartialMatch]
        self._condition = TrueFormula()
        # matches that were not yet pushed to the parent for further processing
        self._unhandled_partial_matches = Queue()

    def consume_first_partial_match(self):
        """
        Removes and returns a single partial match buffered at this node.
        Used in the root node to collect full pattern matches.
        """
        ret = self._partial_matches[0]
        del self._partial_matches[0]
        return ret

    def has_partial_matches(self):
        """
        Returns True if this node contains any partial matches and False otherwise.
        """
        return len(self._partial_matches) > 0

    def get_last_unhandled_partial_match(self):
        """
        Returns the last partial match buffered at this node and not yet transferred to its parent.
        """
        return self._unhandled_partial_matches.get()

    def set_parent(self, parent):
        """
        Sets the parent of this node.
        """
        self._parent = parent

    def clean_expired_partial_matches(self, last_timestamp: datetime):
        """
        Removes partial matches whose earliest timestamp violates the time window constraint.
        """
        if self._sliding_window == timedelta.max:
            return
        self._partial_matches.try_clean_expired_partial_matches(last_timestamp - self._sliding_window)

    def add_partial_match(self, pm: PartialMatch):
        """
        Registers a new partial match at this node.
        In case of DefaultStorage (without optimization) the insertion is by the timestamp, O(log n).
        In case of SortedStorage the insertion is by timestamp or condition, O(log n).
        In case of UnsortedStorage the insertion is directly at the end, O(1).
        """
        self._partial_matches.add(pm)
        if self._parent is not None:
            self._unhandled_partial_matches.put(pm)

    def get_partial_matches(self, value_of_new_pm):
        """
        Returns only partial matches that can be a good fit according the the new partial match received
        from the other node.
        """
        return self._partial_matches.get(value_of_new_pm)

    def get_leaves(self):
        """
        Returns all leaves in this tree - to be implemented by subclasses.
        """
        raise NotImplementedError()

    def apply_formula(self, formula: Formula):
        """
        Applies a given formula on all nodes in this tree - to be implemented by subclasses.
        """
        raise NotImplementedError()

    def get_event_definitions(self):
        """
        Returns the specifications of all events collected by this tree - to be implemented by subclasses.
        """
        raise NotImplementedError()

    def create_storage_unit(self, storage_params: TreeStorageParameters, sorting_key: callable = None,
                            relation_op=None, equation_side=None, sort_by_first_timestamp=False):
        raise NotImplementedError()
