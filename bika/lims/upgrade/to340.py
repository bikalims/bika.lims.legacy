# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import transaction
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.idserver import generateUniqueId
from bika.lims.numbergenerator import INumberGenerator
from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zope.component import getUtility


def upgrade(tool):
    """Upgrade step to 3.4.0
    """
    portal = aq_parent(aq_inner(tool))

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '3.4.0'))

    pc = getToolByName(portal, 'portal_catalog')
    #Do nothing other than prepare for 3.4.0
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'content')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'rolemap')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')

    return True


