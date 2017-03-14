# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import SelectionWidget as _s


class SelectionWidget(_s):
    _properties = _s._properties.copy()
    _properties.update({
        'macro': "bika_widgets/selection",
    })

    security = ClassSecurityInfo()

registerWidget(SelectionWidget)
