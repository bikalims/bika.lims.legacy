# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeWidget
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
# noinspection PyUnresolvedReferences
from bika.lims.config import ATTACHMENT_REPORT_OPTIONS, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((
    ComputedField(
        'RequestID',
        expression='here.getRequestID()',
        widget=ComputedWidget(
            visible=True,
        ),
    ),
    FileField(
        'AttachmentFile',
        widget=FileWidget(
            label=_("Attachment"),
        ),
    ),
    UIDReferenceField(
        'AttachmentType',
        required=0,
        allowed_types=('AttachmentType',),
        widget=ReferenceWidget(
            label=_("Attachment Type"),
        ),
    ),
    StringField(
        'ReportOption',
        searchable=True,
        vocabulary="ATTACHMENT_REPORT_OPTIONS",
        widget=SelectionWidget(
            label=_("Report Options"),
            checkbox_bound=0,
            format='select',
            visible=True,
            default='a',
        ),
    ),
    StringField(
        'AttachmentKeys',
        searchable=True,
        widget=StringWidget(
            label=_("Attachment Keys"),
        ),
    ),
    DateTimeField(
        'DateLoaded',
        required=1,
        default_method='current_date',
        widget=DateTimeWidget(
            label=_("Date Loaded"),
        ),
    ),
    ComputedField(
        'AttachmentTypeUID',
        expression="context.getAttachmentType().UID() if "
                   "context.getAttachmentType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'ClientUID',
        expression='here.aq_parent.UID()',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
),
)

schema['id'].required = False
schema['title'].required = False


class Attachment(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Id """
        return safe_unicode(self.getId()).encode('utf-8')

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()


atapi.registerType(Attachment, PROJECTNAME)
