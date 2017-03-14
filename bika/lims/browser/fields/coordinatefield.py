# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordField
from Products.Archetypes.Registry import registerField

from bika.lims import bikaMessageFactory as _


class CoordinateField(RecordField):
    """ Stores angle in deg, min, sec, bearing """
    security = ClassSecurityInfo()
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'angle',
        'subfields' : ('degrees', 'minutes', 'seconds', 'bearing'),
##        'required_subfields' : ('degrees', 'minutes', 'seconds', 'bearing'),
        'subfield_labels':{'degrees':_('Degrees'),
                           'minutes':_('Minutes'),
                           'seconds':_('Seconds'),
                           'bearing':_('Bearing')},
        'subfield_sizes': {'degrees':3,
                           'minutes':2,
                           'seconds':2,
                           'bearing':1},
        'subfield_validators' : {'degrees':'coordinatevalidator',
                                 'minutes':'coordinatevalidator',
                                 'seconds':'coordinatevalidator',
                                 'bearing':'coordinatevalidator',},
        })

registerField(CoordinateField,
              title = "Coordinate",
              description = "Used for storing coordinates",
              )
