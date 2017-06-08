# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName


class ClientSamplePointsView(BikaListingView):
    """This is displayed in the "Sample Points" tab on each client
    """

    def __init__(self, context, request):
        super(ClientSamplePointsView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'SamplePoint',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "SamplePoints"
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/samplepoint_big.png"
        self.title = self.context.translate(_("Sample Points"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title',
                      'replace_url': 'absolute_url'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
            'Sample Types': {'title': _('Sample Types'),},
            'Composite': {'title': _('Composite'),},
            'Sampling Frequency': {'title': _('Sampling Frequency'),},
            'Attachments': {'title': _('Attachments'),
                      'replace_url': 'absolute_url'},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'Description', 'Sample Types', 'Composite',
                         'Sampling Frequency', 'Attachments']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title', 'Description', 'Sample Types', 'Composite',
                         'Sampling Frequency', 'Attachments']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title', 'Description', 'Sample Types', 'Composite',
                         'Sampling Frequency', 'Attachments']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddSamplePoint, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=SamplePoint',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientSamplePointsView, self).__call__()

    def folderitem(self, obj, item, index):
        item['replace']['title'] = "<a href='%s'>%s</a>" % \
             (item['url'], item['title'])
        item['Description'] = obj.Description()
        titles = [st.Title() for st in obj.getSampleTypes()]
        item['Sample Types'] = ",".join(titles)
        if obj.aq_parent.portal_type == 'Client':
            item['Owner'] = obj.aq_parent.Title()
        else:
            item['Owner'] = self.context.bika_setup.laboratory.Title()
        item['Composite'] = 'Y' if obj.Composite else 'N'
        sample_freq = obj.SamplingFrequency.keys()
        sample_freq.sort()
        sample_freq_str = ''
        for value in sample_freq:
            sample_freq_str += '%s %s ' % (
                            value.title(), obj.SamplingFrequency[value])
        item['Sampling Frequency'] = sample_freq_str
        item['replace']['Attachments'] = \
                        "<a href='%s/at_download/Attachment'>%s</a>" % \
                             (item['url'], obj.AttachmentFile.filename)
        return item
