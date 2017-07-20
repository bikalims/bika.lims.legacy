# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone.supermodel import model
from plone.dexterity.content import Container
from zope.interface import implements
from bika.lims.browser.bika_listing import BikaListingView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.interfaces import IClientTypes
from bika.lims import bikaMessageFactory as _


class ClientTypesView(BikaListingView):
    """Displays all system's sampling rounds
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ClientTypesView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {'portal_type': 'ClientType',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': '++add++ClientType',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Client Types"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/clienttype_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "clienttype"

        self.columns = {
            'Title': {'title': _('Type'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         ]},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         ]},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         ]},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for item in items:
            obj = item.get("obj", None)
            if obj is None:
                continue
            item['Description'] = obj.Description()
            item['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (item['url'], item['Title'])

        return items


class ClientTypes(Container):
    implements(IClientTypes)
    displayContentsTab = False
