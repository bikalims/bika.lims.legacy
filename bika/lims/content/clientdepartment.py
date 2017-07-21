# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_base
from plone.supermodel import model
from plone.dexterity.content import Container, Item
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import ILabContact, IBikaSetupCatalog

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView

from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.schema import RelationChoice, RelationList

class IClientDepartment(model.Schema):
    """ A Client Departments container.
    """

class ClientDepartment(Item):
    implements(IClientDepartment)

    # Catalog Multiplex support
    def _catalogs(self):
        ''' catalogs we will use '''
        return [getToolByName(self, 'portal_catalog'),
                getToolByName(self, 'bika_setup_catalog')]

@indexer(IClientDepartment, IBikaSetupCatalog)
def clienttype_title_indexer(obj):
    if obj.title:
        return obj.title

@indexer(IClientDepartment, IBikaSetupCatalog)
def clienttype_sortable_title_indexer(obj):
    if obj.title:
        return [w.lower() for w in obj.title.split(' ')]
