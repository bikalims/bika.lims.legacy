# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from decimal import Decimal, InvalidOperation

from Products.CMFCore.utils import getToolByName
from zope.component import getAdapters

from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import t


class ResultOutOfRangeIcons(object):
    """An icon provider for DuplicateAnalysis: Result field out-of-range alerts
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):

        translate = self.context.translate
        path = "++resource++bika.lims.images"
        alerts = {}
        for name, adapter in getAdapters((self.context, ), IResultOutOfRange):
            ret = adapter(result, **kwargs)
            if not ret:
                continue
            out_of_range = ret["out_of_range"]
            spec = ret["spec_values"]
            if out_of_range:
                message = t(_("Relative percentage difference, ${variation_here} %, is out of valid range (${variation} %))",
                      mapping={'variation_here': ret['variation_here'], 'variation': ret['variation'], } ))
                alerts[self.context.UID()] = [
                    {
                        'msg': message,
                        'field': 'Result',
                        'icon': path + '/exclamation.png',
                    },
                ]
                break
        return alerts


class ResultOutOfRange(object):
    """An icon provider for DuplicateAnalysis: Result field out-of-range alerts
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        translate = self.context.translate
        # Other types of analysis depend on Analysis base class, and therefore
        # also provide IAnalysis.  We allow them to register their own adapters
        # for range checking, and manually ignore them here.
        if self.context.portal_type != 'DuplicateAnalysis':
            return None
        workflow = getToolByName(self.context, 'portal_workflow')
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return None
        result = result is not None and str(result) or self.context.getResult()
        # We get the form_result for our duplicated analysis in **kwargs[orig]
        # If not, then use the database value.
        if 'form_results' in kwargs:
            auid = self.context.getAnalysis().UID()
            orig = kwargs.get('form_results', {}).get(auid)
        else:
            orig = self.context.getAnalysis().getResult()
        try:
            result = Decimal(str(result))
            orig = Decimal(str(orig))
            variation = Decimal(
                str(self.context.getService().getDuplicateVariation()))
        except (TypeError, ValueError, InvalidOperation):
            return None
        duplicates_average = Decimal((orig+result)/2)
        duplicates_diff = Decimal(abs(orig-result))
        try:
            variation_here = Decimal((duplicates_diff/duplicates_average)*100)
        except ZeroDivisionError:
            variation_here = Decimal(0)
        variation_qty = Decimal(duplicates_diff/2)
        tolerance_allowed = Decimal(((duplicates_average * variation) / 100) / 2)
        # range_min = orig - (orig * variation / 100)
        # range_max = orig + (orig * variation / 100)
        range_min = duplicates_average - tolerance_allowed
        range_max = duplicates_average + tolerance_allowed
        spec = {"min": range_min,
                "max": range_max,
                "error": 0,
                }
        # if range_min <= result <= range_max:
        if variation_here > variation :
            out_of_range = True
            acceptable = True
        else:
            out_of_range = False
            acceptable = True
        return {'out_of_range':out_of_range,
                'acceptable': acceptable,
                'spec_values': spec,
                'variation_here': variation_here,
                'variation': variation,
                }
