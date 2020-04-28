from abc import ABC
from queue import Queue
from datetime import timedelta, datetime
from base.Formula import TrueFormula, Formula
from evaluation.PartialMatch import PartialMatch
from misc.Utils import find_partial_match_by_timestamp
from evaluation.Storage import Storage


class Node(ABC):
    """
    This class represents a single node of an evaluation tree.
    """

    def __init__(self, sliding_window: timedelta, parent):
        self._parent = parent
        self._sliding_window = sliding_window
        self._partial_matches: Storage[PartialMatch]
        self._condition = TrueFormula()
        self._unhandled_partial_matches = Queue()
        # matches that were not yet pushed to the parent for further processing

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
        return self._unhandled_partial_matches.get()  # returns it and removes it

    def set_parent(self, parent):
        """
        Sets the parent of this node.
        """
        self._parent = parent

    # this function should be simplified to call the clean up in the storage
    def clean_expired_partial_matches(self, last_timestamp: datetime):
        """
        Removes partial matches whose earliest timestamp violates the time window constraint.
        """
        if self._sliding_window == timedelta.max:
            return
        count = find_partial_match_by_timestamp(  # binary search: sorted by first timestmap of partial match
            self._partial_matches, last_timestamp - self._sliding_window
        )
        self._partial_matches = self._partial_matches[count:]

    def add_partial_match(self, pm: PartialMatch):
        """
        Registers a new partial match at this node.
        As of now, the insertion is always by the timestamp, and the partial matches are stored in a list sorted by
        timestamp. Therefore, the insertion operation is performed in O(log n).
        """
        raise NotImplementedError()

    """'MUH"""

    def create_storage_unit(self):
        raise NotImplementedError()

    # def set_sorting_properties(self):
    #    raise NotImplementedError()

    """'MUH"""

    def get_partial_matches(
        self, new_pm: PartialMatch, new_pm_key: callable, Greater=None
    ):
        """
        Returns the currently stored partial matches.
        """
        """
        Returns the currently stored partial matches.
        """
        if Greater is None:
            return self._partial_matches
        elif Greater is True:
            return self._partial_matches.get_greater(new_pm_key(new_pm))
        elif Greater is False:
            return self._partial_matches.get_smaller(new_pm_key(new_pm))
        raise ValueError()

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

    def create_storage_units(self, leaf_index=-1):
        """
        creates a storage container for the PMs, the container sorts the PMs according to the condition Formula - to be implemented by subclasses. 
        """
        raise NotImplementedError()
