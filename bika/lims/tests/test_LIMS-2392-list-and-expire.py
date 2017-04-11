# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.ATContentTypes.utils import dt2DT
from datetime import datetime, timedelta
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import logger
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaSimpleTestCase
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone import api
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

    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, tmpID())
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        super(TestExpireReferenceSamples, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_LIMS_2392_expire_reference_sample(self):
        self.supplier = self.addthing(self.portal.bika_setup.bika_suppliers,
                                        'Supplier', title='Test Supplier')
        yesterday = datetime.today() - timedelta(days=2)
        yesterday = dt2DT(yesterday)
        ref_sample = self.addthing(self.supplier, 'ReferenceSample',
                title='Test RefSample', DateExpired=yesterday)
        transaction.commit()
        ref_sample.setExpiryDate(yesterday)
        ref_sample.reindexObject()
        transaction.commit()

        browser = self.getBrowser()
        browser.addHeader('Authorization', 'Basic admin:secret')
        portal = self.getPortal()
        portal_url = portal.absolute_url()
        state = api.content.get_state(ref_sample)
        if state != 'current':
            self.fail("State is %s and not current" % state)

        expire_refs_url = portal_url + '/@@expire_reference_samples'
        browser.open(expire_refs_url)
        content = browser.contents
        expected_content = 'Expired 1 Reference Samples'
        if content != expected_content:
            self.fail(
                    "Expected: %s but got %s" % (expected_content,content))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExpireReferenceSamples))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
