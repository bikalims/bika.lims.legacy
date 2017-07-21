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

@indexer(IClientType, IBikaSetupCatalog)
def clienttype_title_indexer(obj):
    if obj.title:
        return obj.title

@indexer(IClientType, IBikaSetupCatalog)
def clienttype_sortable_title_indexer(obj):
    if obj.title:
        return [w.lower() for w in obj.title.split(' ')]

