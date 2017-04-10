# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import re

from Products.CMFPlone.utils import safe_unicode

from datetime import datetime
from plone import api

from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _

class ExpireReferenceSamplesView(BrowserView):
    """Expireference Samples
    """

    def expire_reference_samples(self):
        workflow = api.portal.get_tool('portal_workflow')
        bc = api.portal.get_tool('bika_catalog')
        query = {'portal_type': 'ReferenceSample',
                 'getExpiryDate': {'query': datetime.today(),
                                   'range': 'max'},
                 'review_state': 'current',
                }
        brains = bc(query)
        cnt = 0
        for brain in brains:
            obj = brain.getObject()
            state = api.content.get_state(obj=brain.getObject())
            try:
                api.content.transition(obj=obj, transition='expire')
                cnt += 1
            except Exception, e:
                path = '/'.join(obj.getPhysicalPath())
                raise RuntimeError('Expire Reference Samples \
                        Could not Expire %s') % path

        return 'Expired %s Reference Samples' % cnt
