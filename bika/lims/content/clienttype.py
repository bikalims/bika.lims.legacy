# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from zope.interface import implements

from plone.indexer import indexer
from plone.dexterity.content import Item

from bika.lims.interfaces import IClientType
from bika.lims.interfaces import IBikaSetupCatalog


class ClientType(Item):
    implements(IClientType)

    # Bika catalog multiplex for Dexterity contents
    # please see event handlers in bika.lims.subscribers.catalogobject
    _bika_catalogs = [
        "bika_setup_catalog"
    ]


@indexer(IClientType, IBikaSetupCatalog)
def clienttype_title_indexer(obj):
    if obj.title:
        return obj.title


@indexer(IClientType, IBikaSetupCatalog)
def clienttype_sortable_title_indexer(obj):
    if obj.title:
        return [w.lower() for w in obj.title.split(' ')]
