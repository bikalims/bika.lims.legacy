# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_base
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IBikaSetupCatalog, IClientType
from plone.dexterity.content import Container, Item
from plone.indexer import indexer
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope import schema

class ClientType(Item):
    implements(IClientType)

    # Catalog Multiplex support
    def _catalogs(self):
        ''' catalogs we will use '''
        return [getToolByName(self, 'portal_catalog'),
                getToolByName(self, 'bika_setup_catalog')]

    def indexObject(self):
        ''' index an object on all registered catalogs '''
        for c in self._catalogs():
            c.catalog_object(self)

    def unindexObject(self):
        ''' remove an object from all registered catalogs '''
        path = '/'.join(self.getPhysicalPath())
        for c in self._catalogs():
            c.uncatalog_object(path)

    def reindexObjectSecurity(self, skip_self=False):
        ''' reindex only security information on catalogs '''
        path = '/'.join(self.getPhysicalPath())
        for c in self._catalogs():
            for brain in c.unrestrictedSearchResults(path=path):
                brain_path = brain.getPath()
                if brain_path == path and skip_self:
                    continue
                # Get the object
                ob = brain._unrestrictedGetObject()

                # Recatalog with the same catalog uid.
                # _cmf_security_indexes in CMFCatalogAware
                c.reindexObject(ob,
                                idxs=self._cmf_security_indexes,
                                update_metadata=0,
                                uid=brain_path)

    def reindexObject(self, idxs=[]):
        ''' reindex object '''
        if idxs == []:
            # Update the modification date.
            if hasattr(aq_base(self), 'notifyModified'):
                self.notifyModified()
        for c in self._catalogs():
            if c is not None:
                c.reindexObject(self,
                                idxs=idxs)

@indexer(IClientType, IBikaSetupCatalog)
def clienttype_title_indexer(obj):
    if obj.title:
        return obj.title

@indexer(IClientType, IBikaSetupCatalog)
def clienttype_sortable_title_indexer(obj):
    if obj.title:
        return [w.lower() for w in obj.title.split(' ')]

