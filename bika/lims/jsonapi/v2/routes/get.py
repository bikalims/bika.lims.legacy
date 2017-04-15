# -*- coding: utf-8 -*-

from bika.lims.jsonapi import api
from bika.lims.jsonapi import url_for
from bika.lims.jsonapi import add_route
from bika.lims.jsonapi.exceptions import APIError


@add_route("/v2/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/<string:route>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/<string:route>/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
def get(context, request, route=None, uid=None):
    """
    """
    resource_mapping = api.get_resource_mapping()
    portal_type = resource_mapping.get(route)

    if api.is_uid(route):
        return api.get_batched(uid=route)
    elif portal_type is not None:
        return api.get_batched(portal_type=portal_type, uid=uid)
    else:
        raise APIError(404, "Not Found")
