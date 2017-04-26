# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import unittest

import transaction
from Products.CMFPlone.FactoryTool import _createObjectByType
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from bika.lims.api import get_bika_setup, do_transition_for
from bika.lims.api import get_portal
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaSimpleTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest

class test_FormattedResult(BikaSimpleTestCase):
    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, 'tmp')
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        super(test_FormattedResult, self).setUp()
        portal = get_portal()
        bika_setup = get_bika_setup()
        login(self.portal, TEST_USER_NAME)
        self.client = self.addthing(
            portal.clients, 'Client', title='Happy Hills', ClientID='HH')
        self.contact = self.addthing(
            self.client, 'Contact', Firstname='Rita', Lastname='Mohale')
        self.sampletype = self.addthing(
            bika_setup.bika_sampletypes, 'SampleType', Prefix='H2O')
        self.service = self.addthing(
            bika_setup.bika_analysisservices, 'AnalysisService',
            title='Calcium', Keyword='Ca')
        transaction.commit()

    def tearDown(self):
        super(test_FormattedResult, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_LIMS_2221_DecimalMarkWithSciNotation(self):
        # Notations
        # '1' => aE+b / aE-b
        # '2' => ax10^b / ax10^-b
        # '3' => ax10^b / ax10^-b (with superscript)
        # '4' => a·10^b / a·10^-b
        # '5' => a·10^b / a·10^-b (with superscript)
        matrix = [
            # as_prec  as_exp not mark  result          formatted result
            # -------  ------ --- ----  ------          ----------------
            [0,        0,     1,  ',',  '0',            '0'],
            [0,        0,     2,  ',',  '0',            '0'],
            [0,        0,     3,  ',',  '0',            '0'],
            [0,        0,     4,  ',',  '0',            '0'],
            [0,        0,     5,  ',',  '0',            '0'],
            [2,        5,     1,  ',',  '0.01',         '0,01'],
            [2,        5,     2,  ',',  '0.01',         '0,01'],
            [2,        5,     3,  ',',  '0.01',         '0,01'],
            [2,        5,     4,  ',',  '0.01',         '0,01'],
            [2,        5,     5,  ',',  '0.01',         '0,01'],
            [2,        1,     1,  ',',  '0.123',        '1,2e-01'],
            [2,        1,     2,  ',',  '0.123',        '1,2x10^-1'],
            [2,        1,     3,  ',',  '0.123',        '1,2x10<sup>-1</sup>'],
            [2,        1,     4,  ',',  '0.123',        '1,2·10^-1'],
            [2,        1,     5,  ',',  '0.123',        '1,2·10<sup>-1</sup>'],
            [2,        1,     1,  ',',  '1.234',        '1,23'],
            [2,        1,     2,  ',',  '1.234',        '1,23'],
            [2,        1,     3,  ',',  '1.234',        '1,23'],
            [2,        1,     4,  ',',  '1.234',        '1,23'],
            [2,        1,     5,  ',',  '1.234',        '1,23'],
            [2,        1,     1,  ',',  '12.345',       '1,235e01'],
            [2,        1,     2,  ',',  '12.345',       '1,235x10^1'],
            [2,        1,     3,  ',',  '12.345',       '1,235x10<sup>1</sup>'],
            [2,        1,     4,  ',',  '12.345',       '1,235·10^1'],
            [2,        1,     5,  ',',  '12.345',       '1,235·10<sup>1</sup>'],
            [4,        3,     1,  ',',  '-123.45678',   '-123,4568'],
            [4,        3,     2,  ',',  '-123.45678',   '-123,4568'],
            [4,        3,     3,  ',',  '-123.45678',   '-123,4568'],
            [4,        3,     4,  ',',  '-123.45678',   '-123,4568'],
            [4,        3,     5,  ',',  '-123.45678',   '-123,4568'],
            [4,        3,     1,  ',',  '-1234.5678',   '-1,2345678e03'],
            [4,        3,     2,  ',',  '-1234.5678',   '-1,2345678x10^3'],
            [4,        3,     3,  ',',  '-1234.5678',   '-1,2345678x10<sup>3</sup>'],
            [4,        3,     4,  ',',  '-1234.5678',   '-1,2345678·10^3'],
            [4,        3,     5,  ',',  '-1234.5678',   '-1,2345678·10<sup>3</sup>'],
        ]
        serv = self.service
        serv.setLowerDetectionLimit('-99999')  # test results below 0 too
        prevm = []
        an = None
        bs = get_bika_setup()
        for m in matrix:
            as_prec = m[0]
            as_exp = m[1]
            notation = m[2]
            _dm = m[3]
            _result = m[4]
            _expected = m[5]
            bs.setResultsDecimalMark(_dm)
            # Create the AR and set the values to the AS, but only if necessary
            if not an or prevm[0] != as_prec or prevm[1] != as_exp:
                serv.setPrecision(as_prec)
                serv.setExponentialFormatPrecision(as_exp)
                self.assertEqual(serv.getPrecision(), as_prec)
                self.assertEqual(
                    serv.Schema().getField('Precision').get(serv), as_prec)
                self.assertEqual(serv.getExponentialFormatPrecision(), as_exp)
                self.assertEqual(
                    serv.Schema().getField(
                        'ExponentialFormatPrecision').get(serv), as_exp)
                values = {'Client': self.client.UID(),
                          'Contact': self.client.getContacts()[0].UID(),
                          'SamplingDate': '2015-01-01',
                          'SampleType': self.sampletype.UID()}
                ar = create_analysisrequest(self.client, {}, values,
                                            [serv.UID()])
                do_transition_for(ar, 'receive')
                an = ar.getAnalyses()[0].getObject()
                prevm = m
            an.setResult(_result)

            self.assertEqual(an.getResult(), _result)
            self.assertEqual(an.Schema().getField('Result').get(an), _result)
            decimalmark = bs.getResultsDecimalMark()
            try:
                fr = an.getFormattedResult(sciformat=notation,
                                           decimalmark=decimalmark)
                self.assertEqual(fr, _expected)
            except:
                import pdb; pdb.set_trace()
                fr = an.getFormattedResult(sciformat=notation,
                                           decimalmark=decimalmark)
                self.assertEqual(fr, _expected)

    def test_LIMS_2371_SignificantFigures(self):

        RESULT_VALUES = {
            '-22770264':    {1: '-2e07', 2: '-2.3e07', 3: '-2.28e07', 4: '-2.277e07', 5: '-2.277e07', 6: '-2.27703e07', 7: '-2.277026e07'},
            '-2277.3':      {1: '-2000', 2: '-2300', 3: '-2280', 4: '-2277', 5: '-2277.3', 6: '-2277.30', 7: '-2277.300'},
            '-40277':       {1: '-40000', 2: '-40000', 3: '-40300', 4: '-40280', 5: '-40277', 6: '-40277.0', 7: '-40277.00'},
            '-40277.036':   {1: '-40000', 2: '-40000', 3: '-40300', 4: '-40280', 5: '-40277', 6: '-40277.0', 7: '-40277.04'},
            '47000.01':     {1: '50000', 2: '47000', 3: '47000', 4: '47000', 5: '47000', 6: '47000.0', 7: '47000.01', 8: '47000.010', 9: '47000.0100'},
            '132':          {1: '100', 2: '130', 3: '132', 4: '132.0', 5: '132.00', 6: '132.000'},
            '14700.04':     {1: '10000', 2: '15000', 3: '14700', 4: '14700', 5: '14700', 6: '14700.0', 7: '14700.04', 8: '14700.040', 9: '14700.0400'},
            '1407.0':       {1: '1000', 2: '1400', 3: '1410', 4: '1407', 5: '1407.0', 6: '1407.00', 7: '1407.000'},
            '0.147':        {1: '0.1', 2: '0.15', 3: '0.147', 4: '0.1470', 5: '0.14700'},
            '4308':         {1: '4000', 2: '4300', 3: '4310', 4: '4308', 5: '4308.0', 6: '4308.00', 7: '4308.000'},
            '470000':       {1: '500000', 2: '470000', 3: '470000', 4: '470000', 5: '470000', 6: '470000', 7: '470000.0', 8: '470000.00', 9: '470000.000'},
            '0.154':        {1: '0.2', 2: '0.15', 3: '0.154', 4: '0.1540', 5: '0.15400', 6: '0.154000'},
            '0.166':        {1: '0.2', 2: '0.17', 3: '0.166', 4: '0.1660', 5: '0.16600', 6: '0.166000'},
            '0.156':        {1: '0.2', 2: '0.16', 3: '0.156', 4: '0.1560', 5: '0.15600', 6: '0.156000'},
            '47841242':     {1: '5e07', 2: '4.8e07', 3: '4.78e07', 4: '4.784e07', 5: '4.7841e07', 6: '4.78412e07', 7: '4.784124e07', 8: '4.7841242e07', 9: '4.7841242e07', 10: '4.7841242e07'},
            '2.2e-06':      {1: '0.000002', 2: '0.0000022', 3: '0.00000220', 4: '0.000002200'},
            '19019.19019':  {1: '20000', 2: '19000', 3: '19000', 4: '19020', 5: '19019', 6: '19019.2', 7: '19019.19', 8: '19019.190', 9: '19019.1902', 10: '19019.19019'}
        }

        service = self.service
        service.setExponentialFormatPrecision(7)  # just a high value
        service.setDisplayRounding("SIGNIFICANT_FIGURES")
        service.setLowerDetectionLimit('-999999999')  # Test results below 0 too
        for value, tests in RESULT_VALUES.items():
            # Create the AR with modified analysis service
            for sig_figures, expected in tests.items():
                service.setSignificantFigures(sig_figures)
                ar = create_analysisrequest(
                    self.client,
                    {},
                    {'Client': self.client.UID(),
                     'Contact': self.client.getContacts()[0].UID(),
                     'SamplingDate': '2015-01-01',
                     'SampleType': self.sampletype.UID()},
                    [service.UID()])
                do_transition_for(ar, 'receive')
                an = ar.getAnalyses()[0].getObject()
                an.setResult(value)
                self.assertEqual(an.getFormattedResult(), expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(test_FormattedResult))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
