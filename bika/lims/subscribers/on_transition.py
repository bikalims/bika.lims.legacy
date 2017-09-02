# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import DateTime
from bika.lims import api


def before_transition_handler(instance, event):
    parent = api.get_parent(instance)
    if api.get_portal_type(instance) == "AnalysisRequest":
        update_ar_modification_dates(instance)
    elif api.get_portal_type(parent) == "AnalysisRequest":
        update_ar_modification_dates(parent)
    else:
        update_modification_date(instance)


def update_ar_modification_dates(ar):
    # update the sample modification date
    sample = ar.getSample()
    update_modification_date(sample)

    # update partitions modification date
    for part in ar.getPartitions():
        update_modification_date(part)

    # update attachments modification date
    for att in ar.getAttachment():
        update_modification_date(att)

    # update analyses modification date
    for an in ar.getAnalyses():
        update_modification_date(an)


def update_modification_date(obj):
    """update the modification date of the object"""
    if obj is None:
        return
    obj.setModificationDate(DateTime.DateTime())
