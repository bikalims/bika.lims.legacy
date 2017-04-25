# -*- coding: utf-8 -*-

from bika.lims.jsonapi import api
from bika.lims.jsonapi.v2 import add_route
from bika.lims.jsonapi.exceptions import APIError


@add_route("/<string:resource>",
           "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/<string:resource>/<string(maxlength=32):uid>",
           "bika.lims.jsonapi.v2.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """GET
    """
    # we have a UID as resource, return the record
    if api.is_uid(resource):
        return api.get_record(resource)

    portal_type = api.resource_to_portal_type(resource)
    if portal_type is None:
        raise APIError(404, "Not Found")
    return api.get_batched(portal_type=portal_type, uid=uid, endpoint="bika.lims.jsonapi.v2.get")


# http://werkzeug.pocoo.org/docs/0.11/routing/#builtin-converters
# http://werkzeug.pocoo.org/docs/0.11/routing/#custom-converters
@add_route("/<any(create,update,delete):action>",
           "bika.lims.jsonapi.v2.action", methods=["POST"])
@add_route("/<any(create,update,delete):action>/<string(maxlength=32):uid>",
           "bika.lims.jsonapi.v2.action", methods=["POST"])
@add_route("/<string:resource>/<any(create,update,delete):action>",
           "bika.lims.jsonapi.v2.action", methods=["POST"])
@add_route("/<string:resource>/<string(maxlength=32):uid>/<any(create,update,delete):action>",
           "bika.lims.jsonapi.v2.action", methods=["POST"])
def action(context, request, action=None, resource=None, uid=None):
    """Various HTTP POST actions
    """

    # Fetch and call the action function of the API
    func_name = "{}_items".format(action)
    action_func = getattr(api, func_name, None)
    if action_func is None:
        api.fail(500, "API has no member named '{}'".format(func_name))

    portal_type = api.resource_to_portal_type(resource)
    items = action_func(portal_type=portal_type, uid=uid)

    return {
        "count": len(items),
        "items": items,
        "url": api.url_for("bika.lims.jsonapi.v2.action", action=action),
    }


@add_route("/search",
           "bika.lims.jsonapi.v2.search", methods=["GET"])
def search(context, request):
    """Generic search route

    <Plonesite>/@@API/v2/search -> returns all contents of the portal
    <Plonesite>/@@API/v2/search?portal_type=Folder -> returns only folders
    ...
    """
    return api.get_batched()
