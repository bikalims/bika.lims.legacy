# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Supply Order Folder contains Supply Orders
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from plone.app.folder import folder
from zope.interface import implements

from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.interfaces import ISupplyOrderFolder

schema = folder.ATFolderSchema.copy()


class SupplyOrderFolder(folder.ATFolder):
    implements(ISupplyOrderFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(SupplyOrderFolder, PROJECTNAME)
