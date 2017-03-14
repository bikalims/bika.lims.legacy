# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims.permissions import *


def upgrade(tool):
    """
    issue #615: missing configuration for some add permissions
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))

    # batch permission defaults
    mp = portal.manage_permission
    mp(AddAnalysisSpec, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSamplingDeviation, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSampleMatrix, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    portal.reindexObject()

    return True
