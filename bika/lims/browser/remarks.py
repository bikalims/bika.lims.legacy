# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import plone
from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.intelligenttext.transforms \
    import convertWebIntelligentPlainTextToHtml

from bika.lims.browser import BrowserView


class ajaxSetRemarks(BrowserView):
    """ Modify Remarks field and return new rendered field value
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        field = self.context.Schema()["Remarks"]
        value = self.request['value'].strip() + "\n\n"
        existing = self.context.getRemarks(mimetype='text/x-web-intelligent').strip()

        date = DateTime().rfc822()
        user = getSecurityManager().getUser()
        divider = "=== %s (%s)\n" % (date, user)

        remarks = convertWebIntelligentPlainTextToHtml(divider) + \
            convertWebIntelligentPlainTextToHtml(value) + \
            convertWebIntelligentPlainTextToHtml(existing)

        self.context.setRemarks(divider + value + existing, mimetype='text/x-web-intelligent')

        return remarks.strip()
