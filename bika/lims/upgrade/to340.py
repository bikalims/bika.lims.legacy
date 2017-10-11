# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.api import get_uid
from bika.lims.idserver import generateUniqueId
from bika.lims.numbergenerator import INumberGenerator
from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from Products.CMFPlone.utils import _createObjectByType
from plone.api.portal import get_tool
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

    # Migrate some references (Analysis->*) to new UIDReference
    refactor_references()

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


def refactor_references():
    """
    Many ReferenceFields and HistoryAwareReferenceFields need to be migrated
    away from Archetypes ReferenceField.

    UIDReferenceField uses simple StringFields to store the UIDs. After
    refactoring, the following references were moved to UIDReference:

    Analysis.Attachments
    Analysis.Instrument
    Analysis.Method
    Analysis.SamplePartition
    """
    migrate_refs('AnalysisInstrument', 'Instrument')
    migrate_refs('AnalysisMethod', 'Method')
    migrate_refs('AnalysisAttachment', 'Attachment')
    migrate_refs('AnalysisSamplePartition', 'SamplePartition')

    refs_removed = 0
    for rel in ['AnalysisInstrument',
                'AnalysisMethod',
                'AnalysisAttachment',
                'AnalysisSamplePartition',
                ]:
        refs_removed += del_at_refs(rel)
    if refs_removed:
        logger.info("Total reference objects removed: %s" % refs_removed)


def touidref(src, dst, src_relation, fieldname):
    """Convert an archetypes reference in src/src_relation to a UIDReference
    in dst/fieldname.
    """
    field = dst.getField(fieldname)
    refs = src.getRefs(relationship=src_relation)
    if len(refs) == 1:
        value = get_uid(refs[0])
    elif len(refs) > 1:
        value = filter(lambda x: x, [get_uid(ref) for ref in refs])
    else:
        value = field.get(src)
    if not value:
        value = ''
    if not field:
        raise Exception('Cannot find field %s/%s' % (fieldname, src))
    if field.required and not value:
        logger.error('Required %s field %s/%s has no value' % (
            src.portal_type, src, fieldname))
    field.set(src, value)


def migrate_refs(rel, fieldname, pgthreshold=100):
    rc = get_tool('reference_catalog')
    uc = get_tool('uid_catalog')
    refs = rc(relationship=rel)
    if refs:
        logger.info('Migrating %s references of %s' % (len(refs), rel))
    for i, ref in enumerate(refs):
        obj = uc(UID=ref[1])
        if obj:
            obj = obj[0].getObject()
            if i and not divmod(i, pgthreshold)[1]:
                logger.info("%s/%s %s/%s" % (i, len(refs), obj, rel))
            touidref(obj, obj, rel, fieldname)


def del_at_refs(rel):
    # Remove this relation from at_references
    rc = get_tool('reference_catalog')
    refs = rc(relationship=rel)
    removed = 0
    size = 0
    if refs:
        logger.info("Found %s refs for %s" % (len(refs), rel))
        ref_dict = {ref[0]: ref.getObject() for ref in refs}
        for ref_id, ref_obj in ref_dict.items():
            removed += 1
            size += 1
            ref_obj.aq_parent.manage_delObjects([ref_id])
    if removed:
        logger.info("Performed %s deletions" % removed)
    return removed
