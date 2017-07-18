# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from plone import protect

from Products.Five.browser import BrowserView

from bika.lims import api
from bika.lims import logger
from bika.lims.config import ATTACHMENT_REPORT_OPTIONS
from bika.lims.decorators import returns_json
from bika.lims.permissions import AddAttachment
from bika.lims.permissions import EditResults
from bika.lims.permissions import EditFieldResults

EDITABLE_STATES = [
    'to_be_sampled',
    'to_be_preserved',
    'sample_due',
    'sample_received',
    'to_be_verified',
]


class AttachmentsView(BrowserView):
    """Manage view for attachments
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """get called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    def __call__(self):
        """Endpoint for form actions etc.
        """
        protect.CheckAuthenticator(self.request.form)

        if not self.request.form.get("submitted", False):
            return self.request.response.redirect(self.context.absolute_url())

        if len(self.traverse_subpath) != 1:
            return self.request.response.redirect(self.context.absolute_url())

        func_name = self.traverse_subpath[0]
        action_name = "action_{}".format(func_name)
        action = getattr(self, action_name, None)

        if action is None:
            logger.warn("AttachmentsView.__call__: Unknown action name '{}'"
                        .format(func_name))
            return self.request.response.redirect(self.context.absolute_url())

        return action()

    def action_update(self):
        """Form action to update the attachments
        """
        form = self.request.form
        # order = form.get("order", [])

        attachments = form.get("attachments", [])
        for attachment in attachments:
            # attachment is a form mapping, not a dictionary -> convert
            values = dict(attachment)

            uid = values.pop("UID")
            obj = api.get_object_by_uid(uid)

            # delete the attachment if the delete flag is true
            if values.pop("delete", False):
                self.delete_attachment(obj)
                continue

            # update the attachment with the given data
            obj.update(**values)
            obj.reindexObject()

        return self.request.response.redirect(self.context.absolute_url())

    def action_add(self):
        """Form action to add a new attachment
        """
        form = self.request.form
        parent = api.get_parent(self.context)
        this_file = form.get('AttachmentFile_file', None)

        # nothing to do if the attachment file is missing
        if this_file is None:
            logger.warn("AttachmentView.action_add_attachment: Attachment file is missing")
            return

        # create attachment
        attachmentid = self.context.generateUniqueId('Attachment')
        attachment = api.create(parent, "Attachment", id=attachmentid)

        attachment.edit(
            AttachmentFile=this_file,
            AttachmentType=self.request.form.get('AttachmentType', ''),
            AttachmentKeys=self.request.form.get('AttachmentKeys', ''),
            ReportOption=self.request.form.get('ReportOption', 'a'),
        )

        attachment.processForm()
        attachment.reindexObject()

        analysis_uid = form.get("Analysis", None)
        if analysis_uid:
            rc = api.get_tool("reference_catalog")
            analysis = rc.lookupObject(analysis_uid)
            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)

            if api.get_workflow_status_of(analysis) == 'attachment_due':
                api.do_transition_form(analysis, 'attach')
        else:
            others = self.context.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.context.setAttachment(attachments)

        if self.request['HTTP_REFERER'].endswith('manage_results'):
            self.request.response.redirect('{}/manage_results'.format(
                self.context.absolute_url()))
        else:
            self.request.response.redirect(self.context.absolute_url())

    def delete_attachment(self, attachment):
        """Delete attachment
        """
        uid = attachment.UID()

        parent_ar = attachment.getRequest()
        parent_an = attachment.getAnalysis()
        parent = parent_an if parent_an else parent_ar
        others = parent.getAttachment()

        # remove references
        attachments = []
        for other in others:
            if other.UID() != uid:
                attachments.append(other.UID())
        parent.setAttachment(attachments)

        # delete the attachment finally
        client = api.get_parent(attachment)
        client.manage_delObjects([attachment.getId(), ])

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


class ajaxAttachmentsView(AttachmentsView):
    """Ajax helpers for attachments
    """

    def __init__(self, context, request):
        super(ajaxAttachmentsView, self).__init__(context, request)

    @returns_json
    def __call__(self):
        protect.CheckAuthenticator(self.request.form)

        if len(self.traverse_subpath) != 1:
            return self.error("Not found", status=404)
        func_name = "ajax_{}".format(self.traverse_subpath[0])
        func = getattr(self, func_name, None)
        if func is None:
            return self.error("Invalid function", status=400)
        return func()

    def error(self, message, status=500, **kw):
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message}
        result.update(kw)
        return result

    def ajax_delete_analysis_attachment(self):
        form = self.request.form
        attachment_uid = form.get('attachment_uid', None)
        if not attachment_uid:
            return "error"
        uc = api.get_tool('uid_catalog')
        attachment = uc(UID=attachment_uid)
        if not attachment:
            return "%s does not exist" % attachment_uid
        attachment = attachment[0].getObject()
        for analysis in attachment.getBackReferences("AnalysisAttachment"):
            analysis.setAttachment([r for r in analysis.getAttachment()
                                    if r.UID() != attachment.UID()])
        for analysis in attachment.getBackReferences("DuplicateAnalysisAttachment"):
            analysis.setAttachment([r for r in analysis.getAttachment()
                                    if r.UID() != attachment.UID()])
        attachment.aq_parent.manage_delObjects(ids=[attachment.getId(), ])
        return "success"
