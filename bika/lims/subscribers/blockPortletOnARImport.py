from zope.component import getMultiAdapter, getUtility
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

#The object/content has to have ILocalPortletAssignable interface implemented
#if it does not already have it so that you don't get a ComponentLookupError
def blockPortletsUpponARImportCreation(content, event):
    manager = getUtility(IPortletManager, name='plone.rightcolumn')
    assignable = getMultiAdapter((content, manager), ILocalPortletAssignmentManager)
    for category in (GROUP_CATEGORY, CONTENT_TYPE_CATEGORY,CONTEXT_CATEGORY,USER_CATEGORY):
        assignable.setBlacklistStatus(category, 1)
