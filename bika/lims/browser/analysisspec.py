# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from zope.component import adapts
from zope.interface import implements

from bika.lims.interfaces import IAnalysisSpec
from bika.lims.interfaces import IJSONReadExtender


class JSONReadExtender(object):
    """Adds the UID to the ResultsRange dict.  This will go away
    when we stop using keywords for this stuff.
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisSpec)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        bsc = self.context.bika_setup_catalog
        rr = []
        for i, x in enumerate(data.get("ResultsRange", [])):
            keyword = x.get("keyword")
            proxies = bsc(portal_type="AnalysisService", getKeyword=keyword)
            if proxies:
                data['ResultsRange'][i]['uid'] = proxies[0].UID
