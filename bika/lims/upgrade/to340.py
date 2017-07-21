# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.idserver import generateUniqueId
from bika.lims.numbergenerator import INumberGenerator
from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from Products.CMFPlone.utils import _createObjectByType
from zope.component import getUtility


def upgrade(tool):
    """Upgrade step to 3.4.0
    """
    portal = aq_parent(aq_inner(tool))

    qi = portal.portal_quickinstaller
    setup = portal.portal_setup
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '3.4.0'))

    #Do nothing other than prepare for 3.4.0
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'content')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'rolemap')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    
    # Sync the empty number generator with existing content
    prepare_number_generator(portal)

    return True


def prepare_number_generator(portal):
    # Load IDServer defaults

    config_map = [
        {'context': 'sample',
         'counter_reference': 'AnalysisRequestSample',
         'counter_type': 'backreference',
         'form': '{sampleId}-R{seq:02d}',
         'portal_type': 'AnalysisRequest',
         'prefix': '',
         'sequence_type': 'counter',
         'split_length': ''},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'B-{seq:03d}',
         'portal_type': 'Batch',
         'prefix': 'batch',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': '{sampleType}-{seq:04d}',
         'portal_type': 'Sample',
         'prefix': 'sample',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'WS-{seq:03d}',
         'portal_type': 'Worksheet',
         'prefix': 'worksheet',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'I-{seq:03d}',
         'portal_type': 'Invoice',
         'prefix': 'invoice',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'AI-{seq:03d}',
         'portal_type': 'ARImport',
         'prefix': 'arimport',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'QC-{seq:03d}',
         'portal_type': 'ReferenceSample',
         'prefix': 'refsample',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'SA-{seq:03d}',
         'portal_type': 'ReferenceAnalysis',
         'prefix': 'refanalysis',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'D-{seq:03d}',
         'portal_type': 'DuplicateAnalysis',
         'prefix': 'duplicate',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': 'sample',
         'counter_reference': 'SamplePartition',
         'counter_type': 'contained',
         'form': '{sampleId}-P{seq:d}',
         'portal_type': 'SamplePartition',
         'prefix': '',
         'sequence_type': 'counter',
         'split_length': ''}]
    # portal.bika_setup.setIDFormatting(config_map)

    # Regenerate every id to prime the number generator
    bsc = portal.bika_setup_catalog
    for brain in bsc():
        generateUniqueId(brain.getObject())

    pc = portal.portal_catalog
    for brain in pc():
        generateUniqueId(brain.getObject())
