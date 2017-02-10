# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IInstruments
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements


class InstrumentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Instrument',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Instrument',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Instruments"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrument_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Instrument'),
                      'index': 'sortable_title'},
            'Type': {'title': _('Type'),
                     'index': 'getInstrumentTypeName',
                     'toggle': True,
                     'sortable': True},
            'Brand': {'title': _('Brand'),
                      'toggle': True},
            'Model': {'title': _('Model'),
                      'index': 'getModel',
                      'toggle': True},
            'ExpiryDate': {'title': _('Expiry Date'),
                           'toggle': True},
            'WeeksToExpire': {'title': _('Weeks To Expire'),
                              'toggle': False},
            'Methods': {'title': _('Methods'),
                       'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate',
                         'WeeksToExpire',
                         'Methods']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate',
                         'WeeksToExpire',
                         'Methods']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate',
                         'WeeksToExpire',
                         'Methods']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)

        for item in items:
            obj = item.get("obj", None)
            if obj is None:
                continue

            itype = obj.getInstrumentType()
            item['Type'] = itype.Title() if itype else ''
            ibrand = obj.getManufacturer()
            item['Brand'] = ibrand.Title() if ibrand else ''
            item['Model'] = obj.getModel()

            data = obj.getCertificateExpireDate()
            if data == '':
                item['ExpiryDate'] = "No date avaliable"
            else:
                item['ExpiryDate'] = data.asdatetime().strftime(self.date_format_short)

            if obj.isOutOfDate():
                item['WeeksToExpire'] = "Out of date"
            else:
                date = int(str(obj.getWeeksToExpire()).split(',')[0].split(' ')[0])
                weeks, days = divmod(date, 7)
                item['WeeksToExpire'] = str(weeks) + " weeks" + " " + str(days) + " days"

            # Multiple Methods per Instrument handling
            methods = obj.getMethods()
            urls = []
            titles = []
            for method in methods:
                url = method.absolute_url()
                title = method.Title()
                titles.append(title)
                urls.append("<a href='{0}'>{1}</a>".format(url, title))

            item["Methods"] = ", ".join(titles)
            item["replace"]["Methods"] = ", ".join(urls)
            item["replace"]["Title"] = "<a href='{0}'>{1}</a>".format(
                obj.absolute_url(), obj.Title())

        return items

schema = ATFolderSchema.copy()


class Instruments(ATFolder):
    implements(IInstruments)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Instruments, PROJECTNAME)
