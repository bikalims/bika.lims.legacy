# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import DecimalWidget as _d

_marker = []


class DecimalWidget(_d):
    _properties = _d._properties.copy()
    _properties.update({
        'macro': "bika_widgets/decimal",
        'unit': '',
    })

    security = ClassSecurityInfo()


registerWidget(DecimalWidget,
               title='Decimal',
               description=('Renders a HTML text input box which '
                            'accepts a fixed point value'),
               )

registerPropertyType('unit', 'string', DecimalWidget)
