# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims import api
from bika.lims.permissions import AddAttachment
from bika.lims.permissions import EditResults
from bika.lims.permissions import EditFieldResults
from bika.lims.config import ATTACHMENT_REPORT_OPTIONS

EDITABLE_STATES = [
    'to_be_sampled',
    'to_be_preserved',
    'sample_due',
    'sample_received',
    'to_be_verified',
]
CACHE_CONTROL = 'no-cache, no-store, must-revalidate, post-check=0, pre-check=0'


class AttachmentsViewlet(ViewletBase):
    """Viewlet to manage Attachments
    """
    template = ViewPageTemplateFile("templates/attachments.pt")

    def global_attachments_allowed(self):
        """Checks Bika Setup if Attachments are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getAttachmentsPermitted()

    def global_ar_attachments_allowed(self):
        """Checks Bika Setup if AR Attachments are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getARAttachmentsPermitted()

    def global_analysis_attachments_allowed(self):
        """Checks Bika Setup if Attachments for Analyses are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getAnalysisAttachmentsPermitted()

    def get_attachments(self):
        """Returns a list of attachments from the AR base view
        """
        context = self.context
        request = self.request
        view = api.get_view("base_view", context=context, request=request)
        return view.getAttachments()

    def get_attachment_types(self):
        """Returns a list of available attachment types
        """
        bika_setup_catalog = api.get_tool("bika_setup_catalog")
        attachment_types = bika_setup_catalog(portal_type='AttachmentType',
                                              inactive_state='active',
                                              sort_on="sortable_title",
                                              sort_order="ascending")
        return attachment_types

    def get_attachment_report_options(self):
        """Returns the valid attachment report options
        """
        return ATTACHMENT_REPORT_OPTIONS.items()

    def get_analyses(self):
        """Returns a list of analyses from the AR
        """
        analyses = self.context.getAnalyses(full_objects=True)
        return filter(self.is_analysis_attachment_allowed, analyses)

    def is_analysis_attachment_allowed(self, analysis):
        """Checks if the analysis
        """
        service = analysis.getService()
        if service.getAttachmentOption() not in ["p", "r"]:
            return False
        if api.get_workflow_status_of(analysis) in ["retracted"]:
            return False
        return True

    def user_can_add_attachments(self):
        """Checks if the current logged in user is allowed to add attachments
        """
        if not self.global_attachments_allowed():
            return False
        context = self.context
        pm = api.get_tool("portal_membership")
        return pm.checkPermission(AddAttachment, context)

    def user_can_update_attachments(self):
        """Checks if the current logged in user is allowed to update attachments
        """
        context = self.context
        pm = api.get_tool("portal_membership")
        return pm.checkPermission(EditResults, context) or \
            pm.checkPermission(EditFieldResults, context)

    def user_can_delete_attachments(self):
        """Checks if the current logged in user is allowed to delete attachments
        """
        context = self.context
        user = api.get_current_user()
        if not self.is_ar_editable():
            return False
        return (self.user_can_add_attachments() and
                not user.allowed(context, ["Client"])) or \
            self.user_can_update_attachments()

    def is_ar_editable(self):
        """Checks if the AR is in a review_state that allows to update the attachments.
        """
        state = api.get_workflow_status_of(self.context)
        return state in EDITABLE_STATES

    def show(self):
        """Controls if the viewlet should be rendered
        """
        url = self.request.getURL()
        # XXX: Hack to show the viewlet only on the AR base_view
        if not any(map(url.endswith, ["base_view", "manage_results"])):
            return False
        return self.user_can_add_attachments() or \
            self.user_can_update_attachments()

    def update(self):
        """Called always before render()
        """
        super(AttachmentsViewlet, self).update()
        self.request.RESPONSE.setHeader('Cache-Control', CACHE_CONTROL)

    def render(self):
        if not self.show():
            return ""
        return self.template()


class WorksheetAttachmentsViewlet(AttachmentsViewlet):
    """Viewlet to manage Attachments on Worksheets
    """
    template = ViewPageTemplateFile("templates/worksheet_attachments.pt")

    def show(self):
        """Controls if the viewlet should be rendered
        """
        # XXX: Hack to show the viewlet only on the WS manage_results view
        if not self.request.getURL().endswith("manage_results"):
            return False
        return True

    def get_attachments(self):
        """Returns a list of Attachment objects
        """
        return []

    def get_services(self):
        """Returns a list of AnalysisService objects
        """
        return self.context.getWorksheetServices()
