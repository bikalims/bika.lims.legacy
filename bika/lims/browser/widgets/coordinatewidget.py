# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
import datetime

class CoordinateWidget(TypesWidget):
    security = ClassSecurityInfo()
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/coordinatewidget",
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""
        empty_marker = {} #This is a hack
        # a poor workaround for Plone repeating itself.
        # XXX this is important XXX
        key = field.getName() + '_value'
        if key in instance.REQUEST:
            return instance.REQUEST[key], {}
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker, {}
        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}

registerWidget(CoordinateWidget,
               title = 'CoordinateWidget',
               description = '',
               )
