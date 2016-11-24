# -*- coding: utf-8 -*-

import types

from AccessControl import ClassSecurityInfo

from Products.Archetypes.Widget import ReferenceWidget

from bika.lims import logger


class SimpleReferenceWidget(ReferenceWidget):
    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):

        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker
        if isinstance(value, types.StringTypes):
            values = [v.strip() for v in value.split('\n')]
        elif isinstance(value, types.ListType):
            # Filter out empty strings to avoid
            # Traceback (innermost last):
            #   [...]
            #   Module bika.lims.browser.fields.historyawarereferencefield, line 87, in set
            #   Module Products.CMFEditions.CopyModifyMergeRepositoryTool, line 136, in isVersionable
            # AttributeError: 'NoneType' object has no attribute 'portal_type'
            values = filter(lambda x: x != '', value)
            logger.debug("BechemReferenceWidget::process_form: Values {0} -> {1}".format(value, values))
        else:
            values = []
        return values, {}
