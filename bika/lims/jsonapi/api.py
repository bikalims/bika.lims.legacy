# -*- coding: utf-8 -*-

from AccessControl import Unauthorized

from Products.CMFPlone.PloneBatch import Batch

from plone.jsonapi.core import router

from bika.lims import api
from bika.lims import logger
from bika.lims.jsonapi.query import search
from bika.lims.jsonapi import request as req
from bika.lims.jsonapi import underscore as _
from bika.lims.jsonapi.interfaces import IInfo
from bika.lims.jsonapi.interfaces import IBatch
from bika.lims.jsonapi.exceptions import APIError
from bika.lims.jsonapi.interfaces import IDataManager

_marker = object()


# GET BATCHED
def get_batched(portal_type=None, uid=None, endpoint=None, **kw):
    """ returns a batched result record (dictionary)
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


def get_search_results(portal_type=None, uid=None, **kw):
    """Search the catalog and return the results

    :returns: Catalog search results
    :rtype: list or Products.ZCatalog.Lazy.LazyMap
    """

    # If we have an UID, return the object immediately
    if uid is not None:
        logger.info("UID '%s' found, returning the object immediately" % uid)
        return _.to_list(api.get_object_by_uid(uid))

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
        results = list(results) + _.to_list(api.get_portal())

    return results


def get_batch(sequence, size, start=0, endpoint=None, complete=False):
    """ create a batched result record out of a sequence (catalog brains)
    """

    # we call an adapter here to allow backwards compatibility hooks
    batch = IBatch(Batch(sequence, size, start))

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
        if include_children and api.is_folderish(brain_or_object):
            info.update(get_children_info(brain_or_object, complete=complete))
        return info

    return map(extract_data, brains_or_objects)


def portal_type_to_resource(portal_type):
    """Converts a portal type name to a pluralized resource name
    """
    resource = portal_type.lower()
    resource = resource.replace(" ", "")
    # if resource.endswith("y"):
    #     resource = resource.rstrip("y")
    #     resource = resource + "ies"
    # elif not resource.endswith("s"):
    #     resource = resource + "s"
    return resource


def get_endpoint(brain_or_object):
    """Calculate the endpoint for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Endpoint for this object (pluralized portal type)
    :rtype: string
    """
    portal_type = api.get_portal_type(brain_or_object)
    resource = portal_type_to_resource(portal_type)
    return resource

    # XXX Hack to get the right namespaced endpoint
    endpoints = router.DefaultRouter.view_functions.keys()
    if resource in endpoints:
        return resource  # exact match
    endpoint_candidates = filter(lambda e: e.endswith(resource), endpoints)
    if len(endpoint_candidates) == 1:
        # only return the namespaced endpoint, if we have an exact match
        return endpoint_candidates[0]
    # default
    return None


def get_resource_mapping():
    """Map resources used in the routes to portal types, e.g.

    analysisrequests -> AnalysisRequest
    analysisservices -> AnalysisService
    laboratories -> Laboratory
    ...
    """
    portal_types = get_portal_types()
    resources = map(portal_type_to_resource, portal_types)
    return dict(zip(resources, portal_types))


def get_portal_types():
    """Get a list of all portal types
    """
    types_tool = api.get_tool("portal_types")
    return types_tool.listContentTypes()


def is_uid(uid):
    """Check if the passed in uid is a valid uid
    """
    if uid == "0":
        return True
    if not isinstance(uid, basestring):
        return False
    if len(uid) != 32:
        return False
    if not uid.isalnum():
        return False
    return True


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


def get_contents(brain_or_object, depth=1):
    """Lookup folder contents for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of contained contents
    :rtype: list/Products.ZCatalog.Lazy.LazyMap
    """

    # Nothing to do if the object is contentish
    if not api.is_folderish(brain_or_object):
        return []

    query = {
        "path": {
            "query": api.get_path(brain_or_object),
            "depth": depth,
        }
    }

    return search(query=query)


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

        # add workflow data if the user requested it
        # -> only possible if `?complete=yes`
        if req.get_workflow(False):
            workflow = get_workflow_info(obj)
            info.update({"workflow": workflow})

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

    uid = api.get_uid(brain_or_object)
    return {
        "uid": uid,
        "url": get_url(brain_or_object),
        "api_url": url_for(endpoint, uid=uid),
    }


def get_url(brain_or_object):
    """Get the absolute Plone URL for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone URL
    :rtype: string
    """
    if api.is_brain(brain_or_object):
        return brain_or_object.getURL()
    return brain_or_object.absolute_url()


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
        # XXX plone.jsonapi.core should catch the BuildError of Werkzeug and
        #     throw another error which can be handled here.
        logger.debug("Could not build API URL for endpoint '%s'. "
                     "No route provider registered?" % endpoint)

        # build generic API URL
        # https://github.com/collective/plone.jsonapi.routes/issues/59
        return router.url_for(default, force_external=True, values=values)


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
    if api.is_portal(brain_or_object):
        return {}

    # get the parent object
    parent = api.get_parent(brain_or_object)

    # fall back if no endpoint specified
    if endpoint is None:
        endpoint = get_endpoint(parent)

    # return portal information
    if api.is_portal(parent):
        return {
            "parent_id": api.get_id(parent),
            "parent_uid": 0,
            "parent_url": url_for("plonesites", uid=0),
        }

    return {
        "parent_id": api.get_id(parent),
        "parent_uid": api.get_uid(parent),
        "parent_url": url_for(endpoint, uid=api.get_uid(parent))
    }


def get_workflow_info(brain_or_object, endpoint=None):
    """Generate workflow information of the (first) assigned workflow

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: Workflow information mapping
    :rtype: dict
    """

    # ensure we have a full content object
    obj = api.get_object(brain_or_object)

    # get the portal workflow tool
    wf_tool = api.get_tool("portal_workflow")

    # the assigned workflows of this object
    wfs = wf_tool.getWorkflowsFor(obj)

    # no worfkflows assigned -> return
    if not wfs:
        return {}

    # get the first one
    workflow = wfs[0]

    # get the status info of the current state (dictionary)
    status = wf_tool.getStatusOf(workflow.getId(), obj)

    # https://github.com/collective/plone.jsonapi.routes/issues/33
    if not status:
        return {}

    # get the current review_status
    current_state_id = status.get("review_state", None)

    # get the wf status object
    current_status = workflow.states[current_state_id]

    # get the title of the current status
    current_state_title = current_status.title

    def to_transition_info(transition):
        """ return the transition information
        """
        return {
            "value": transition["id"],
            "display": transition["description"],
            "url": transition["url"],
        }

    # get the transition informations
    transitions = map(to_transition_info, wf_tool.getTransitionsFor(obj))

    return {
        "workflow": workflow.getId(),
        "status": current_state_title,
        "review_state": current_state_id,
        "transitions": transitions
    }


# -----------------------------------------------------------------------------
#   Functional Helpers
# -----------------------------------------------------------------------------

def validate_object(brain_or_object, data):
    """Validate the entire object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param data: The sharing dictionary as returned from the API
    :type data: dict
    :returns: invalidity status
    :rtype: dict
    """
    obj = api.get_object(brain_or_object)

    # Call the validator of AT Content Types
    if api.is_at_content(obj):
        return obj.validate(data=data)

    return {}


def update_object_with_data(content, record):
    """Update the content with the record data

    :param content: A single folderish catalog brain or content object
    :type content: ATContentType/DexterityContentType/CatalogBrain
    :param record: The data to update
    :type record: dict
    :returns: The updated content object
    :rtype: object
    :raises:
        APIError,
        :class:`~plone.jsonapi.routes.exceptions.APIError`
    """

    # ensure we have a full content object
    content = api.get_object(content)

    # get the proper data manager
    dm = IDataManager(content)

    if dm is None:
        raise APIError(400, "Update for this object is not allowed")

    # https://github.com/collective/plone.jsonapi.routes/issues/77
    # filter out bogus keywords
    field_kwargs = _.omit(record, "file")

    # Iterate through record items
    for k, v in record.items():
        try:
            success = dm.set(k, v, **field_kwargs)
        except Unauthorized:
            raise APIError(401, "Not allowed to set the field '%s'" % k)
        except ValueError, exc:
            raise APIError(400, str(exc))

        if not success:
            logger.warn("update_object_with_data::skipping key=%r", k)
            continue

        logger.debug("update_object_with_data::field %r updated", k)

    # Validate the entire content object
    invalid = validate_object(content, record)
    if invalid:
        raise APIError(400, _.to_json(invalid))

    # do a wf transition
    if record.get("transition", None):
        t = record.get("transition")
        logger.debug(">>> Do Transition '%s' for Object %s", t, content.getId())
        api.do_transition_for(content, t)

    # reindex the object
    content.reindexObject()
    return content
