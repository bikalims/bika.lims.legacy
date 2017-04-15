# -*- coding: utf-8 -*-

from bika.lims.jsonapi import api
from bika.lims.jsonapi import url_for
from bika.lims.jsonapi import add_route
from bika.lims.jsonapi.exceptions import APIError


@add_route("/v2/<string:resource>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/<string:resource>/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """GET
    """
    resource_mapping = api.get_resource_mapping()
    portal_type = resource_mapping.get(resource)

    if portal_type is None:
        raise APIError(404, "Not Found")
    return api.get_batched(portal_type=portal_type, uid=uid, endpoint="bika.lims.jsonapi.v2.get")


@add_route("/v2/<string:resource>/create", "bika.lims.jsonapi.v2.create", methods=["GET", "POST"])
@add_route("/v2/<string:resource>/<string:uid>/create", "bika.lims.jsonapi.v2.create", methods=["GET", "POST"])
def create(context, request, resource=None, uid=None):
    """CREATE
    """
    resource_mapping = api.get_resource_mapping()
    portal_type = resource_mapping.get(resource)

    if portal_type is None:
        raise APIError(404, "Not Found")
    return {}


@add_route("/v2/<string:resource>/update", "bika.lims.jsonapi.v2.update", methods=["GET", "POST"])
@add_route("/v2/<string:resource>/<string:uid>/update", "bika.lims.jsonapi.v2.update", methods=["GET", "POST"])
def update(context, request, resource=None, uid=None):
    """UPDATE
    """
    resource_mapping = api.get_resource_mapping()
    portal_type = resource_mapping.get(resource)

    if portal_type is None:
        raise APIError(404, "Not Found")

    items = api.update_items(portal_type, uid=uid, endpoint="bika.lims.jsonapi.v2.update")
    return {
        # "url": url_for("bika.lims.jsonapi.v2.update"),
        "count": len(items),
        "items": items,
    }


@add_route("/v2/<string:resource>/delete", "bika.lims.jsonapi.v2.delete", methods=["GET", "POST"])
@add_route("/v2/<string:resource>/<string:uid>/delete", "bika.lims.jsonapi.v2.delete", methods=["GET", "POST"])
def delete(context, request, resource=None, uid=None):
    """DELETE
    """
    resource_mapping = api.get_resource_mapping()
    portal_type = resource_mapping.get(resource)

    if portal_type is None:
        raise APIError(404, "Not Found")
    return {}
