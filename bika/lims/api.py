# -*- coding: utf-8 -*-
#
# Bika Framwork API (to be extended)

from Products.ZCatalog.interfaces import ICatalogBrain
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.WorkflowCore import WorkflowException

from zope.security.interfaces import Unauthorized
from zope.component import getMultiAdapter
from zope import globalrequest

from plone.dexterity.interfaces import IDexterityContent
from plone import api as ploneapi
from plone.api.exc import InvalidParameterError

from bika.lims import logger
from bika.lims.utils import functools

def get_tool(name):
    """Get a portal tool by name

    :param name: The name of the tool, e.g. `portal_catalog`
    :type name: string
    :returns: Portal Tool
    :rtype: object
    """
    name = functools.to_string(name)
    try:
        return ploneapi.portal.get_tool(name)
    except InvalidParameterError:
        functools.fail("No tool named '%s' found." % name)


def is_brain(brain_or_object):
    """Checks if the passed in object is a portal catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is a catalog brain
    :rtype: bool
    """
    return ICatalogBrain.providedBy(brain_or_object)


def get_object(brain_or_object):
    """Get the full content object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Content object
    :rtype: object
    """
    if is_brain(brain_or_object):
        return brain_or_object.getObject()
    return brain_or_object


def is_dexterity_content(brain_or_object):
    """Checks if the passed in object is a dexterity content type

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is a dexterity content type
    :rtype: bool
    """
    obj = get_object(brain_or_object)
    return IDexterityContent.providedBy(obj)


def get_schema(brain_or_object):
    """Get the schema of the content

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Schema object
    :rtype: object
    """
    obj = get_object(brain_or_object)
    if is_dexterity_content(obj):
        pt = get_portal_catalog()
        fti = pt.getTypeInfo(obj.portal_type)
        return fti.lookupSchema()
    return obj.Schema()


def get_group(group_or_groupname):
    """Return Plone Group

    :param group_or_groupname: Plone group or the name of the group
    :type groupname:  GroupData/str
    :returns: Plone GroupData
    :rtype: object
    """
    if hasattr(group_or_groupname, "_getGroup"):
        return group_or_groupname
    gtool = get_tool("portal_groups")
    return gtool.getGroupById(functools.to_string(group_or_groupname))


def get_user(user_or_username):
    """Return Plone User

    :param user_or_username: Plone user or user id
    :type groupname:  PloneUser/MemberData/str
    :returns: Plone MemberData
    :rtype: object
    """
    if hasattr(user_or_username, "getUserId"):
        return ploneapi.user.get(user_or_username.getUserId())
    return ploneapi.user.get(userid=functools.to_string(user_or_username))


def get_user_properties(user_or_username):
    """Return User Properties

    :param user_or_username: Plone group identifier
    :type groupname:  PloneUser/MemberData/str
    :returns: Plone MemberData
    :rtype: object
    """
    user = get_user(user_or_username)
    if user is None:
        return {}

    out = {}
    plone_user = user.getUser()
    for sheet in plone_user.listPropertysheets():
        ps = plone_user.getPropertysheet(sheet)
        out.update(dict(ps.propertyItems()))
    return out


def get_users_by_roles(roles=None):
    """Search Plone users by their roles

    :param roles: Plone role name or list of roles
    :type roles:  list/str
    :returns: List of Plone users having the role(s)
    :rtype: object
    """
    roles = functools.to_list(roles)
    mtool = get_tool("portal_membership")
    return mtool.searchForMembers(roles=roles)


def to_display_list(pairs, sort=True, allow_empty=True):
    """Create a Plone DisplayList from list items

    :param allow_empty: Allow to select an empty value
    :type roles:  bool
    :returns: Plone DisplayList
    :rtype: object
    """
    pairs = functools.to_list(pairs)
    if allow_empty:
        pairs.insert(0, ["", ""])
    if sort:
        pairs.sort(lambda x, y: cmp(x[1], y[1]))
    return DisplayList(pairs)


def get_portal():
    """Get the portal object

    :returns: Portal object
    :rtype: object
    """
    return ploneapi.portal.getSite()


def is_root(brain_or_object):
    """Checks if the passed in object is the portal root object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is the portal root object
    :rtype: bool
    """
    return ISiteRoot.providedBy(brain_or_object)


def get_bika_setup():
    """Fetch the `bika_setup` folder.
    """
    portal = get_portal()
    return portal.get("bika_setup")


def get_id(brain_or_object):
    """Get the Plone ID for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone ID
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.getId
    return brain_or_object.getId()


def get_uid(brain_or_object):
    """Get the Plone UID for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone UID
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.UID
    if hasattr(brain_or_object, 'UID') and callable(brain_or_object.UID):
        return brain_or_object.UID()
    raise RuntimeError("get_uid requires an object with a UID")


def move_item_in_folder(folder, item, index=None):
    """Move items in a folder

    :param folder: A folderish content type
    :type folder: ATContentType/DexterityContentType/CatalogBrain
    :param item: A content type in the folder
    :type item: ATContentType/DexterityContentType/CatalogBrain
    :returns: New index of the content type
    :rtype: int
    """
    folder = get_object(folder)
    item = get_object(item)
    item_id = get_id(item)

    if functools.is_digit(index):
        folder.moveObjectToPosition(item_id, index)
    if index == "up":
        folder.moveObjectsUp(functools.to_list(item_id), delta=1)
    if index == "down":
        folder.moveObjectsDown(functools.to_list(item_id), delta=1)
    return folder.getObjectPosition(item_id)


def get_object_by_uid(uid):
    """Find an object by a given UID

    :param uid: The UID of the object to find
    :type uid: string
    :returns: Found Object or None
    :rtype: object
    """

    # nothing to do here
    if uid is None:
        return None

    # we try to find the object with both catalogs
    pc = get_portal_catalog()
    rc = get_tool("reference_catalog")

    # try to find the object with the reference catalog first
    obj = rc and rc.lookupObject(uid)
    if obj:
        return obj

    # try to find the object with the portal catalog
    res = pc(dict(UID=uid))
    if len(res) > 1:
        logger.error("More than one object found for UID=%s" % uid)
        return None
    if not res:
        return None

    return get_object(res[0])


def get_parent(brain_or_object):
    """Locate the parent object of the content/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: parent object
    :rtype: ATContentType/DexterityContentType/PloneSite/CatalogBrain
    """

    if is_brain(brain_or_object):
        parent_path = get_parent_path(brain_or_object)

        # parent is the portal object
        if parent_path == get_path(get_portal()):
            return get_portal()

        # query for the parent path
        pc = get_portal_catalog()
        results = pc(path={
            "query": parent_path,
            "depth": 0})

        # fallback to the object
        if not results:
            return get_object(brain_or_object).aq_parent
        # return the brain
        return results[0]

    return brain_or_object.aq_parent


def get_parent_path(brain_or_object):
    """Calculate the physical parent path of this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Physical path of the parent object
    :rtype: string
    """
    if is_brain(brain_or_object):
        path = get_path(brain_or_object)
        return path.rpartition("/")[0]
    return get_path(brain_or_object.aq_parent)


def get_path(brain_or_object):
    """Calculate the physical path of this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Physical path of the object
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.getPath()
    return "/".join(brain_or_object.getPhysicalPath())


def get_catalog(name="portal_catalog"):
    """Get the portal catalog tool

    :returns: Catalog Tool
    :rtype: object
    """
    # TODO: check for valid catalog names
    return get_tool(name)


def get_fields(brain_or_object):
    """Get the list of fields from the object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of fields
    :rtype: list
    """

    obj = get_object(brain_or_object)
    schema = get_schema(obj)

    if is_dexterity_content(obj):
        # XXX implement properly for Dexterity content types
        return dict.fromkeys(schema.names())
    return dict(zip(schema.keys(), schema.fields()))


def safe_getattr(brain_or_object, attr, default=None):
    """Return the attribute value

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param attr: Attribute name
    :type attr: str
    :returns: Attribute value
    :rtype: obj
    """
    obj = get_object(brain_or_object)
    try:
        value = getattr(obj, attr, default)
        if callable(value):
            return value()
        return value
    except Unauthorized:
        return default


def search(query, catalog="portal_catalog"):
    """Search the named catalog with the given query.

    :param query: A suitable search query.
    :type query: dict
    :param catalog: The named catalog tool
    :type catalog: str
    :returns: Search results
    :rtype: List of ZCatalog brains
    """
    tool = get_tool(catalog)
    return tool(**query)


def get_request():
    """Get the global request object

    :returns: HTTP Request
    :rtype: HTTPRequest object
    """
    return globalrequest.getRequest()


def get_view(name, context=None, request=None):
    """Get the view by name

    :param name: The name of the view
    :type name: str
    :param context: The context to query the view
    :type context: ATContentType/DexterityContentType/CatalogBrain
    :param request: The request to query the view
    :type request: HTTPRequest object
    :returns: HTTP Request
    :rtype: Products.Five.metaclass View object
    """
    context = context or get_portal()
    request = request or get_request()
    return getMultiAdapter((get_object(context), request), name=name)


def get_review_history(brain_or_object, rev=True):
    """Get the review history for the given brain or context.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Workflow history
    :rtype: obj
    """
    obj = get_object(brain_or_object)
    review_history = []
    try:
        workflow = get_tool("portal_workflow")
        review_history = workflow.getInfoFor(obj, 'review_history')
    except WorkflowException:
        return []
    if rev is True:
        return reversed(review_history)
    return review_history
