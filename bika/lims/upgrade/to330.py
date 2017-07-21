# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import api
from bika.lims import logger


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.3.0
    """
    portal = aq_parent(aq_inner(tool))

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '3.3.0'))

    upgrade_attachments_to_blobs(portal)

    return True


def upgrade_attachments_to_blobs(portal):
    """get/set the attachment file fields to migrate existing fields to blob
    """
    logger.info("Upgrading Attachments to Blobs")

    pc = api.get_tool("portal_catalog")
    attachments = map(api.get_object, pc({"portal_type": "Attachment"}))
    for attachment in attachments:
        attachment.setAttachmentFile(attachment.getAttachmentFile())
