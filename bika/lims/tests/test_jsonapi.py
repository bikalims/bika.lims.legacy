# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import doctest
import unittest

from plone.testing import layered
from bika.lims.testing import BIKA_SIMPLE_TESTING

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

DOCTESTS = [
    'bika.lims.jsonapi.request',
    'bika.lims.jsonapi.underscore',
]


def test_suite():
    suite = unittest.TestSuite()
    for module in DOCTESTS:
        suite.addTests([
            layered(doctest.DocTestSuite(module=module, optionflags=OPTIONFLAGS),
                    layer=BIKA_SIMPLE_TESTING),
        ])
    return suite
