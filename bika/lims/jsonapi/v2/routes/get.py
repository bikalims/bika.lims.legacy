# -*- coding: utf-8 -*-

from bika.lims.jsonapi import api
from bika.lims.jsonapi import url_for
from bika.lims.jsonapi import add_route
from bika.lims.jsonapi.exceptions import APIError


@add_route("/v2/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/<string:resource>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/<string:resource>/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """
    """
    resource_mapping = api.get_resource_mapping()
    portal_type = resource_mapping.get(resource)

    if api.is_uid(resource):
        return api.get_batched(uid=resource, endpoint="bika.lims.jsonapi.v2.get")

    elif portal_type is not None:
        return api.get_batched(portal_type=portal_type, uid=uid, endpoint="bika.lims.jsonapi.v2.get")

    else:
        raise APIError(404, "Not Found")
