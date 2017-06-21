# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone.supermodel import model
from plone.dexterity.content import Container, Item
from zope.interface import implements
from bika.lims.browser.bika_listing import BikaListingView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _

from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice, RelationList
from bika.lims.interfaces import ILabContact

class IClientDepartment(model.Schema):
    """ A Client Departments container.
    """

class ClientDepartment(Item):
    implements(IClientDepartment)
    pass
