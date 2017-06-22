# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.idserver import renameAfterCreation
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from datetime import date
from bika.lims.utils.analysisrequest import create_analysisrequest
import unittest
import transaction

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class TestAnalysisRetract(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestAnalysisRetract, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_retract_an_analysis_request_using_profile_price(self):
        #Test the retract process to avoid LIMS-1989
        profs = self.portal.bika_setup.bika_analysisprofiles
        # analysisprofile-1: Trace Metals
        analysisprofile = profs['analysisprofile-1']
        analysisprofile.setUseAnalysisProfilePrice(True)
        analysisprofile.setAnalysisProfilePrice('40.00')
        catalog = getToolByName(self.portal, 'portal_catalog')
        # Getting the first client
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        # Getting some services
        values['Profiles'] = analysisprofile.UID()
        services = catalog(portal_type = 'AnalysisService',
                            inactive_state = 'active')[:3]
        service_uids = [service.getObject().UID() for service in services]
        request = {}
        ar = create_analysisrequest(client, request, values, service_uids)
        transaction.commit()
        all_analyses, all_profiles, analyses_from_profiles = ar.getServicesAndProfiles()
        if len(all_profiles) == 0:
            self.fail('Profiles not being used on the AR')
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')

        # Cheking if everything is going OK
        #import pdb; pdb.set_trace()
        self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'),
                                                        'sample_received')
        for analysis in ar.getAnalyses(full_objects=True):
            analysis.setResult('12')
            wf.doActionFor(analysis, 'submit')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'to_be_verified')
            # retracting results
            wf.doActionFor(analysis, 'retract')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'retracted')

        browser = self.getBrowser()
        invoice_url = '%s/invoice' % ar.absolute_url()
        browser.open(invoice_url)
        if '40.00' not in browser.contents:
            self.fail('Retracted Analyses Services found on the invoice')

    def test_retract_an_analysis_request_without_profile_price(self):
        #Test the retract process to avoid LIMS-1989
        profs = self.portal.bika_setup.bika_analysisprofiles
        # analysisprofile-1: Trace Metals
        analysisprofile = profs['analysisprofile-1']
        catalog = getToolByName(self.portal, 'portal_catalog')
        # Getting the first client
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        # Getting some services
        values['Profiles'] = analysisprofile.UID()
        services = catalog(portal_type = 'AnalysisService',
                            inactive_state = 'active')[:3]
        service_uids = [service.getObject().UID() for service in services]
        request = {}
        ar = create_analysisrequest(client, request, values, service_uids)
        transaction.commit()
        all_analyses, all_profiles, analyses_from_profiles = ar.getServicesAndProfiles()
        if len(all_profiles) == 0:
            self.fail('Profiles not being used on the AR')
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')

        # Cheking if everything is going OK
        #import pdb; pdb.set_trace()
        self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'),
                                                        'sample_received')
        count = 0
        for analysis in ar.getAnalyses(full_objects=True):
            analysis.setResult('12')
            wf.doActionFor(analysis, 'submit')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'to_be_verified')
            # Only retract the first one
            if count == 0:
                wf.doActionFor(analysis, 'retract')
                self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                                'review_state'),'retracted')
            transaction.commit()
            count += 1

        browser = self.getBrowser()
        invoice_url = '%s/invoice' % ar.absolute_url()
        browser.open(invoice_url)
        if '30.00' in browser.contents:
            self.fail('Retracted Analyses Services found on the invoice')
        if '20.00' not in browser.contents:
            self.fail('SubTotal incorrect')


    def test_retract_an_analysis_request(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        services = catalog(portal_type = 'AnalysisService',
                            inactive_state = 'active')[:3]
        service_uids = [service.getObject().UID() for service in services]
        request = {}
        ar = create_analysisrequest(client, request, values, service_uids)
        transaction.commit()
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')

        self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'),
                                                        'sample_received')
        count = 0
        for analysis in ar.getAnalyses(full_objects=True):
            analysis.setResult('12')
            wf.doActionFor(analysis, 'submit')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'to_be_verified')
            # Only retract the first one
            if count == 0:
                wf.doActionFor(analysis, 'retract')
                self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                                'review_state'),'retracted')
            transaction.commit()
            count += 1

        browser = self.getBrowser()
        invoice_url = '%s/invoice' % ar.absolute_url()
        browser.open(invoice_url)
        if '30.00' in browser.contents:
            self.fail('Retracted Analyses Services found on the invoice')
        if '20.00' not in browser.contents:
            self.fail('SubTotal incorrect')

    def tearDown(self):
        logout()
        super(TestAnalysisRetract, self).tearDown()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnalysisRetract))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
