# -*- coding: utf-8 -*-

from bika.lims.jsonapi import api
# from bika.lims.jsonapi import url_for
from bika.lims.jsonapi.v2 import add_route
from bika.lims.jsonapi.exceptions import APIError


@add_route("/<string:resource>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/<string:resource>/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
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
