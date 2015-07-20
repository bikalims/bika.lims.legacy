from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import PMF
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.idserver import renameAfterCreation
from bika.lims.permissions import *
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import encode_header
from bika.lims.utils import isActive
from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, _createObjectByType

import json
import plone
import zope.event


class OrderWorkflowAction(WorkflowAction):

    """Workflow actions taken in Order context.

    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]
        if type(came_from) in (list, tuple):
            came_from = came_from[0]
        # Call out to the workflow action method
        # Use default bika_listing.py/WorkflowAction for other transitions
        method_name = 'workflow_action_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_dispatch(self):
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if not isActive(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return
        # Order publish preview
        self.request.response.redirect(self.context.absolute_url() + "/publish")
