# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import IntegerWidget as _i

_marker = []


class IntegerWidget(_i):
    _properties = _i._properties.copy()
    _properties.update({
        'macro': "bika_widgets/integer",
        'unit': '',
    })

    security = ClassSecurityInfo()

registerWidget(IntegerWidget,
               title='Integer',
               description=('Renders a HTML text input box which '
                            'accepts a integer value'),
               )

registerPropertyType('unit', 'string', IntegerWidget)
