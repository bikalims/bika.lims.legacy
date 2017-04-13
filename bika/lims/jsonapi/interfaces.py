# -*- coding: utf-8 -*-

from zope import interface


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
