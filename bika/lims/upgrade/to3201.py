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
    """Upgrade step required for Bika LIMS 3.2.0
    """
    portal = aq_parent(aq_inner(tool))

    pc = getToolByName(portal, 'portal_catalog')
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '3.2.0'))

    """Updated profile steps
    list of the generic setup import step names: portal.portal_setup.getSortedImportSteps() <---
    if you want more metadata use this: portal.portal_setup.getImportStepMetadata('jsregistry') <---
    important info about upgrade steps in
    http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    """
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    # Rebuild catalog for ClientDepartmentUID
    pc.clearFindAndRebuild()


    typestool = getToolByName(portal, 'portal_types')
    qi = portal.portal_quickinstaller
    if not portal['bika_setup'].get('bika_clientdepartments'):
        typestool.constructContent(type_name="ClientDepartments",
                                   container=portal['bika_setup'],
                                   id='bika_clientdepartments',
                                   title='Client Departments')
    obj = portal['bika_setup']['bika_clientdepartments']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    if not portal['bika_setup'].get('bika_clientdepartments'):
        logger.info("Client Departments not created")

    return True



def departments(portal):
    """ To add department indexes to the catalogs """
    bc = getToolByName(portal, 'bika_catalog')
    if 'getDepartmentUIDs' not in bc.indexes():
        bc.addIndex('getDepartmentUIDs', 'KeywordIndex')
        bc.clearFindAndRebuild()
    bac = getToolByName(portal, 'bika_analysis_catalog')
    if 'getDepartmentUID' not in bac.indexes():
        bac.addIndex('getDepartmentUID', 'KeywordIndex')






def instrument_multiple_methods(portal):
    # An instrument had only a single relevant field called "Method".
    # This field has been replaced with a multiValued "Methods" field.

    # First adding new index
    bsc = getToolByName(portal, 'bika_setup_catalog')
    try:
        bsc.addIndex('getMethodUIDs', 'KeywordIndex')
    except CatalogError:
        # Index already exists form previous run of upgrade step
        pass

    for instrument in portal.bika_setup.bika_instruments.objectValues():
        value = instrument.Schema().get("Method", None).get(instrument)
        if value and type(value) not in (list, tuple):
            # Only listify the value if it's not already listified
            instrument.setMethods([value])

