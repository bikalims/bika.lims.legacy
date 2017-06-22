# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
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


def upgrade(tool):
    """
    """
    portal = aq_parent(aq_inner(tool))

    pc = getToolByName(portal, 'portal_catalog')

    """Updated profile steps
    list of the generic setup import step names: portal.portal_setup.getSortedImportSteps() <---
    if you want more metadata use this: portal.portal_setup.getImportStepMetadata('jsregistry') <---
    important info about upgrade steps in
    http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    """
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'content')
    # Rebuild catalog for ClientDepartmentUID
    pc.clearFindAndRebuild()

    return True
