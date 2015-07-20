from bika.lims.adapters.referencewidgetvocabulary import DefaultReferenceWidgetVocabulary
from bika.lims.jsonapi import get_include_fields
from bika.lims.jsonapi import load_brain_metadata
from bika.lims.jsonapi import load_field_values
from bika.lims.utils import dicts_to_dict
from bika.lims.interfaces import IOrder
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.permissions import *
from bika.lims.workflow import get_workflow_actions
from bika.lims.vocabularies import CatalogVocabulary
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from plone.app.layout.globals.interfaces import IViewView
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getAdapters
from zope.component import queryUtility
from zope.interface import implements

import json

from .workflow import OrderWorkflowAction


class SupplierContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        parent = self.context.aq_parent
        return super(SupplierContactVocabularyFactory, self).__call__(
            portal_type='Supplier',
            path={'query': "/".join(parent.getPhysicalPath()),
                  'level': 0}
        )


class mailto_link_from_contacts:

    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        contacts = field.get(self.context)
        if not type(contacts) in (list, tuple):
            contacts = [contacts, ]
        ret = []
        for contact in contacts:
            if contact:
                mailto = "<a href='mailto:%s'>%s</a>" % (
                    contact.getEmailAddress(), contact.getFullname())
            ret.append(mailto)
        return ",".join(ret)

def mailto_link_from_ccemails(ccemails):
    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        ccemails = field.get(self.context)
        addresses = ccemails.split(",")
        ret = []
        for address in addresses:
            mailto = "<a href='mailto:%s'>%s</a>" % (
                address, address)
            ret.append(mailto)
        return ",".join(ret)


