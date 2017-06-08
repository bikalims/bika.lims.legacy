# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import json

from Acquisition import aq_inner

from Products.Archetypes.browser.validation import InlineValidationView as BaseValidationView
from Products.CMFCore.utils import getToolByName


SKIP_VALIDATION_FIELDTYPES = ('image', 'file', 'datetime', 'reference')


class InlineValidationView(BaseValidationView):

    def __call__(self, uid, fname, value):
        """Validate a given field. Return any error messages.
        """

        res = {'errmsg': ''}

        rc = getToolByName(aq_inner(self.context), 'reference_catalog')
        instance = rc.lookupObject(uid)
        # make sure this works for portal_factory items
        if instance is None:
            instance = self.context

        field = instance.getField(fname)
        if field and field.type not in SKIP_VALIDATION_FIELDTYPES:
            return super(InlineValidationView, self).__call__(uid, fname, value)

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(res)
