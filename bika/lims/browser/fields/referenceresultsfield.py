# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField

from bika.lims import bikaMessageFactory as _


class ReferenceResultsField(RecordsField):

    """a list of reference sample results """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type': 'referenceresult',
        'subfields': ('uid', 'result', 'min', 'max', 'error'),
        'subfield_labels': {'uid': _('Analysis Service'),
                           'result': _('Expected Result'),
                           'error': _('Permitted Error %'),
                           'min': _('Min'),
                           'max': _('Max')},
        })
    security = ClassSecurityInfo()

registerField(ReferenceResultsField,
              title="Reference Values",
              description="Used for storing reference results",
              )
