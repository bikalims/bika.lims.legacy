# -*- coding: utf-8 -*-

from zope import interface


class IInfo(interface.Interface):
    """JSON Info Interface for Portal contents
    """

    def to_dict():
        """Return the dictionary representation of the object
        """

    def __call__():
        """Return the dictionary representation of the object
        """


class IDataManager(interface.Interface):
    """A Data Manager is able to set/get the values of a field.
    """

    def get(name):
        """Get the value of the named field
        """

    def set(name, value):
        """Set the value of the named field
        """


class IBatch(interface.Interface):
    """Plone Batch Interface
    """

    def get_batch():
        """Get the wrapped batch object
        """

    def get_pagesize():
        """Get the current page size
        """

    def get_pagenumber():
        """Get the current page number
        """

    def get_numpages():
        """Get the current number of pages
        """

    def get_sequence_length():
        """Get the length
        """

    def make_next_url():
        """Build and return the next url
        """

    def make_prev_url():
        """Build and return the previous url
        """
