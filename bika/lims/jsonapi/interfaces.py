# -*- coding: utf-8 -*-

from zope import interface


class ICatalog(interface.Interface):
    """ Plone catalog interface
    """

    def search(query):
        """ search the catalog and return the results
        """

    def get_catalog():
        """ get the used catalog tool
        """

    def get_indexes():
        """ get all indexes managed by this catalog
        """

    def get_index(name):
        """ get an index by name
        """

    def to_index_value(value, index):
        """ Convert the value for a given index
        """


class ICatalogQuery(interface.Interface):
    """ Plone catalog query interface
    """

    def make_query(**kw):
        """ create a new query or augment an given query
        """


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
    """A Data Manager is able to set/get the values of the content.
    """

    def get(name):
        """Get the value of the named field
        """

    def set(name, value):
        """Set the value of the named field
        """


class IFieldManager(interface.Interface):
    """A Field Manager is able to set/get the values of a single field.
    """

    def get(instance, **kwargs):
        """Get the value of the field
        """

    def set(instance, value, **kwargs):
        """Set the value of the field
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
