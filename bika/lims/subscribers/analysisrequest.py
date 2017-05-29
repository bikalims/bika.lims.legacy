# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

def ObjectInitializedEventHandler(instance, event):

    if instance.portal_type != "AnalysisRequest":
        return

    priority = instance.getPriority()
    if priority:
        return

    instance.setDefaultPriority()
    return
