# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordWidget
from Products.Archetypes.Registry import registerWidget
import datetime

class CoordinateWidget(RecordWidget):
    security = ClassSecurityInfo()
    _properties = RecordWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/coordinatewidget",
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            value = {}
        if emptyReturnsMarker and not value:
            value = {}
        return value, {}

registerWidget(CoordinateWidget,
               title = 'CoordinateWidget',
               description = '',
               )
