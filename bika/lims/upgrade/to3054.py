from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')

    return True
