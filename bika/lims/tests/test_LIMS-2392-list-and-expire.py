# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.CMFPlone.utils import _createObjectByType
from bika.lims import logger
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaSimpleTestCase
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName

import re
import transaction
import unittest
from plone.app.testing import setRoles

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestExpireReferenceSamples(BikaSimpleTestCase):

    def test_LIMS_2392_expire_reference_sample_is_callable(self):
        browser = self.getBrowser()
        browser.addHeader('Authorization', 'Basic admin:secret')
        portal = self.getPortal()
        portal_url = portal.absolute_url()
        expire_refs_url = portal.absolute_url() + '/@@expire_reference_samples'
        browser.open(expire_refs_url)
        content = browser.contents
        if content != 'Expired 0 Reference Samples':
            self.fail("Expected: Expired 0 Reference Samples but got %s") % \
                    content


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExpireReferenceSamples))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
