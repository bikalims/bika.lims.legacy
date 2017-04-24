# -*- coding: utf-8 -*-

# from AccessControl import Unauthorized

from Products.CMFPlone.PloneBatch import Batch

from plone.jsonapi.core import router

from bika.lims import api
from bika.lims import logger
from bika.lims.jsonapi import request as req
from bika.lims.jsonapi import underscore as _
from bika.lims.jsonapi.interfaces import IInfo
from bika.lims.jsonapi.interfaces import IBatch
from bika.lims.jsonapi.interfaces import ICatalog
from bika.lims.jsonapi.exceptions import APIError
# from bika.lims.jsonapi.interfaces import IDataManager
from bika.lims.jsonapi.interfaces import ICatalogQuery

_marker = object()


# -----------------------------------------------------------------------------
#   JSON API (CRUD) Functions
# -----------------------------------------------------------------------------


# GET BATCHED
def get_batched(portal_type=None, uid=None, endpoint=None, **kw):
    """Get batched results
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid, **kw)

    # fetch the batch params from the request
    size = req.get_batch_size()
    start = req.get_batch_start()

    # check for existing complete flag
    complete = req.get_complete(default=_marker)
    if complete is _marker:
        # if the uid is given, get the complete information set
        complete = uid and True or False

    # return a batched record
    return get_batch(results, size, start, endpoint=endpoint,
                     complete=complete)


# -----------------------------------------------------------------------------
#   Data Functions
# -----------------------------------------------------------------------------

def make_items_for(brains_or_objects, endpoint=None, complete=False):
    """Generate API compatible data items for the given list of brains/objects

    :param brains_or_objects: List of objects or brains
    :type brains_or_objects: list/Products.ZCatalog.Lazy.LazyMap
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: A list of extracted data items
    :rtype: list
    """

    # check if the user wants to include children
    include_children = req.get_children(False)

    def extract_data(brain_or_object):
        info = get_info(brain_or_object, endpoint=endpoint, complete=complete)
        if include_children and is_folderish(brain_or_object):
            info.update(get_children_info(brain_or_object, complete=complete))
        return info

    return map(extract_data, brains_or_objects)


def get_info(brain_or_object, endpoint=None, complete=False):
    """Extract the data from the catalog brain or object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: Data mapping for the object/catalog brain
    :rtype: dict
    """

    # extract the data from the initial object with the proper adapter
    info = IInfo(brain_or_object).to_dict()

    # update with url info (always included)
    url_info = get_url_info(brain_or_object, endpoint)
    info.update(url_info)

    # include the parent url info
    parent = get_parent_info(brain_or_object)
    info.update(parent)

    # add the complete data of the object if requested
    # -> requires to wake up the object if it is a catalog brain
    if complete:
        # ensure we have a full content object
        obj = api.get_object(brain_or_object)
        # get the compatible adapter
        adapter = IInfo(obj)
        # update the data set with the complete information
        info.update(adapter.to_dict())

        # # add workflow data if the user requested it
        # # -> only possible if `?complete=yes`
        # if req.get_workflow(False):
        #     workflow = get_workflow_info(obj)
        #     info.update({"workflow": workflow})

        # # add sharing data if the user requested it
        # # -> only possible if `?complete=yes`
        # if req.get_sharing(False):
        #     sharing = get_sharing_info(obj)
        #     info.update({"sharing": sharing})

    return info


def get_url_info(brain_or_object, endpoint=None):
    """Generate url information for the content object/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: URL information mapping
    :rtype: dict
    """

    # If no endpoint was given, guess the endpoint by portal type
    if endpoint is None:
        endpoint = get_endpoint(brain_or_object)

    uid = get_uid(brain_or_object)
    portal_type = get_portal_type(brain_or_object)
    resource = portal_type_to_resource(portal_type)

    return {
        "uid": uid,
        "url": get_url(brain_or_object),
        "api_url": url_for(endpoint, resource=resource, uid=uid),
    }


def get_parent_info(brain_or_object, endpoint=None):
    """Generate url information for the parent object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: URL information mapping
    :rtype: dict
    """

    # special case for the portal object
    if is_root(brain_or_object):
        return {}

    # get the parent object
    parent = get_parent(brain_or_object)
    portal_type = get_portal_type(parent)
    resource = portal_type_to_resource(portal_type)

    # fall back if no endpoint specified
    if endpoint is None:
        endpoint = get_endpoint(parent)

    return {
        "parent_id": get_id(parent),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, resource=resource, uid=get_uid(parent))
    }


def get_children_info(brain_or_object, complete=False):
    """Generate data items of the contained contents

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: info mapping of contained content items
    :rtype: list
    """

    # fetch the contents (if folderish)
    children = get_contents(brain_or_object)

    def extract_data(brain_or_object):
        return get_info(brain_or_object, complete=complete)
    items = map(extract_data, children)

    return {
        "children_count": len(items),
        "children": items
    }


# -----------------------------------------------------------------------------
#   Batching Helpers
# -----------------------------------------------------------------------------

def get_batch(sequence, size, start=0, endpoint=None, complete=False):
    """ create a batched result record out of a sequence (catalog brains)
    """

    batch = make_batch(sequence, size, start)

    return {
        "pagesize": batch.get_pagesize(),
        "next": batch.make_next_url(),
        "previous": batch.make_prev_url(),
        "page": batch.get_pagenumber(),
        "pages": batch.get_numpages(),
        "count": batch.get_sequence_length(),
        "items": make_items_for([b for b in batch.get_batch()],
                                endpoint, complete=complete),
    }


def make_batch(sequence, size=25, start=0):
    """Make a batch of the given size from the sequence
    """
    # we call an adapter here to allow backwards compatibility hooks
    return IBatch(Batch(sequence, size, start))


# -----------------------------------------------------------------------------
#   API
# -----------------------------------------------------------------------------

def fail(status, msg):
    """API Error
    """
    if msg is None:
        msg = "Reason not given."
    raise APIError(status, "{}".format(msg))


def search(**kw):
    """Search the catalog adapter

    :returns: Catalog search results
    :rtype: iterable
    """
    portal = get_portal()
    catalog = ICatalog(portal)
    catalog_query = ICatalogQuery(catalog)
    query = catalog_query.make_query(**kw)
    return catalog(query)


def get_search_results(portal_type=None, uid=None, **kw):
    """Search the catalog and return the results

    :returns: Catalog search results
    :rtype: iterable
    """

    # If we have an UID, return the object immediately
    if uid is not None:
        logger.info("UID '%s' found, returning the object immediately" % uid)
        return _.to_list(get_object_by_uid(uid))

    # allow to search search for the Plone Site with portal_type
    include_portal = False
    if _.to_string(portal_type) == "Plone Site":
        include_portal = True

    # The request may contain a list of portal_types, e.g.
    # `?portal_type=Document&portal_type=Plone Site`
    if "Plone Site" in _.to_list(req.get("portal_type")):
        include_portal = True

    # Build and execute a catalog query
    results = search(portal_type=portal_type, uid=uid, **kw)

    if include_portal:
        results = list(results) + _.to_list(get_portal())

    return results


def get_portal():
    """Proxy to bika.lims.api.get_portal
    """
    return api.get_portal()


def get_tool(name, default=_marker):
    """Proxy to bika.lims.api.get_tool
    """
    return api.get_tool(name, default)


def get_object(brain_or_object):
    """Proxy to bika.lims.api.get_object
    """
    return api.get_object(brain_or_object)


def is_brain(brain_or_object):
    """Proxy to bika.lims.api.is_brain
    """
    return api.is_brain(brain_or_object)


def is_root(brain_or_object):
    """Proxy to bika.lims.api.is_portal
    """
    return api.is_portal(brain_or_object)


def is_folderish(brain_or_object):
    """Proxy to bika.lims.api.is_folderish
    """
    return api.is_folderish(brain_or_object)


def is_uid(uid):
    """Checks if the passed in uid is a valid UID

    :param uid: The uid to check
    :type uid: string
    :return: True if the uid is a valid 32 alphanumeric uid or '0'
    :rtype: bool
    """
    if not isinstance(uid, basestring):
        return False
    if uid != "0" and len(uid) != 32:
        return False
    return True


def get_contents(brain_or_object, depth=1):
    """Lookup folder contents for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of contained contents
    :rtype: list/Products.ZCatalog.Lazy.LazyMap
    """

    # Nothing to do if the object is contentish
    if not is_folderish(brain_or_object):
        return []

    query = {
        "path": {
            "query": get_path(brain_or_object),
            "depth": depth,
        }
    }

    return search(query=query)


def get_parent(brain_or_object):
    """Locate the parent object of the content/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: parent object
    :rtype: Parent content
    """

    if is_root(brain_or_object):
        return get_portal()

    if is_brain(brain_or_object):
        parent_path = get_parent_path(brain_or_object)
        return get_object_by_path(parent_path)

    return brain_or_object.aq_parent


def get_object_by_uid(uid):
    """Proxy to bika.lims.api.get_object_by_uid
    """
    return api.get_object_by_uid(uid)


def get_path(brain_or_object):
    """Proxy to bika.lims.api.get_path
    """
    return api.get_path(brain_or_object)


def get_parent_path(brain_or_object):
    """Proxy to bika.lims.api.get_parent_path
    """
    return api.get_parent_path(brain_or_object)


def get_portal():
    """Proxy to bika.lims.api.get_portal
    """
    return api.get_portal()


def get_id(brain_or_object):
    """Proxy to bika.lims.api.get_id
    """
    return api.get_id(brain_or_object)


def get_uid(brain_or_object):
    """Proxy to bika.lims.api.get_uid
    """
    return api.get_uid(brain_or_object)


def get_url(brain_or_object):
    """Proxy to bika.lims.api.get_url
    """
    return api.get_url(brain_or_object)


def get_portal_type(brain_or_object):
    """Proxy to bika.lims.api.get_portal_type
    """
    return api.get_portal_type(brain_or_object)


def get_portal_types():
    """Get a list of all portal types

    :retruns: List of portal type names
    :rtype: list
    """
    types_tool = get_tool("portal_types")
    return types_tool.listContentTypes()


def get_resource_mapping():
    """Map resources used in the routes to portal types

    :returns: Mapping of resource->portal_type
    :rtype: dict
    """
    portal_types = get_portal_types()
    resources = map(portal_type_to_resource, portal_types)
    return dict(zip(resources, portal_types))


def portal_type_to_resource(portal_type):
    """Converts a portal type name to a resource name

    :param portal_type: Portal type name
    :type name: string
    :returns: Resource name as it is used in the content route
    :rtype: string
    """
    resource = portal_type.lower()
    resource = resource.replace(" ", "")
    return resource


def resource_to_portal_type(resource):
    """Converts a resource to a portal type

    :param resource: Resource name as it is used in the content route
    :type name: string
    :returns: Portal type name
    :rtype: string
    """
    if resource is None:
        return None

    resource_mapping = get_resource_mapping()
    portal_type = resource_mapping.get(resource.lower())

    if portal_type is None:
        logger.warn("Could not map the resource '{}' "
                    "to any known portal type".format(resource))

    return portal_type


def url_for(endpoint, default="bika.lims.jsonapi.v2.get", **values):
    """Looks up the API URL for the given endpoint

    :param endpoint: The name of the registered route (aka endpoint)
    :type endpoint: string
    :returns: External URL for this endpoint
    :rtype: string/None
    """

    try:
        return router.url_for(endpoint, force_external=True, values=values)
    except Exception:
        logger.warn("Could not build API URL for endpoint '%s'. "
                    "No route provider registered?" % endpoint)
        # build generic API URL
        return router.url_for(default, force_external=True, values=values)


def get_endpoint(brain_or_object, default="bika.lims.jsonapi.v2.get"):
    """Calculate the endpoint for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Endpoint for this object
    :rtype: string
    """
    portal_type = get_portal_type(brain_or_object)
    resource = portal_type_to_resource(portal_type)

    # Try to get the right namespaced endpoint
    endpoints = router.DefaultRouter.view_functions.keys()
    if resource in endpoints:
        return resource  # exact match
    endpoint_candidates = filter(lambda e: e.endswith(resource), endpoints)
    if len(endpoint_candidates) == 1:
        # only return the namespaced endpoint, if we have an exact match
        return endpoint_candidates[0]

    return default


def get_catalog():
    """Get catalog adapter

    :returns: ICatalog adapter for the Portakl
    :rtype: CatalogTool
    """
    portal = get_portal()
    return ICatalog(portal)


def get_object_by_record(record):
    """Find an object by a given record

    Inspects request the record to locate an object

    :param record: A dictionary representation of an object
    :type record: dict
    :returns: Found Object or None
    :rtype: object
    """

    # nothing to do here
    if not record:
        return None

    if record.get("uid"):
        return get_object_by_uid(record["uid"])
    if record.get("path"):
        return get_object_by_path(record["path"])
    if record.get("parent_path") and record.get("id"):
        path = "/".join([record["parent_path"], record["id"]])
        return get_object_by_path(path)

    logger.warn("get_object_by_record::No object found! record='%r'" % record)
    return None


def get_object_by_path(path):
    """Find an object by a given physical path

    :param path: The physical path of the object to find
    :type path: string
    :returns: Found Object or None
    :rtype: object
    """

    # nothing to do here
    if not path:
        return None

    portal = get_portal()
    portal_path = get_path(portal)

    if not path.startswith(portal_path):
        raise APIError(404, "Not a physical path inside the portal")

    if path == portal_path:
        return portal

    return portal.restrictedTraverse(path)
