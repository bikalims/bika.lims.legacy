# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent

import transaction
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.ZCatalog.Catalog import CatalogError

from bika.lims import logger
from Products.CMFCore import permissions
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from bika.lims.permissions import *
from bika.lims.utils import tmpID
from plone import api
from bika.lims.interfaces import IARImport, IAnalysisRequest


from zope.component import getMultiAdapter, getUtility
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

def upgrade(tool):
    """Upgrade step required for Bika LIMS
    """
    disableRightColumnOnARImportView()

    return True

def disableRightColumnOnARImportView():
    arimports = api.content.find(object_provides=IARImport.__identifier__)
    for arimport in arimports:
        obj = arimport.getObject()
        manager = getUtility(IPortletManager, name='plone.rightcolumn')
        assignable = getMultiAdapter((obj, manager), ILocalPortletAssignmentManager)
        for category in (GROUP_CATEGORY, CONTENT_TYPE_CATEGORY,CONTEXT_CATEGORY,USER_CATEGORY):
            assignable.setBlacklistStatus(category, 1)

