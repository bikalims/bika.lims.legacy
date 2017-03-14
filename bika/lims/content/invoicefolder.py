# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import folder
from Products.Archetypes import atapi
from zope.interface import implements

from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IInvoiceFolder, IHaveNoBreadCrumbs

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view':'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view':'invisible'}


class InvoiceFolder(folder.ATFolder):
    implements(IInvoiceFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


atapi.registerType(InvoiceFolder, PROJECTNAME)
