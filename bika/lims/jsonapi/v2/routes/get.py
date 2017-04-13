# -*- coding: utf-8 -*-

from bika.lims.jsonapi import url_for
from bika.lims.jsonapi import add_route


@add_route("/v2/get", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/get/<string:uid>", "bika.lims.jsonapi.v2.get", methods=["GET"])
@add_route("/v2/get/<string:portal_type>", "bika.lims.jsonapi.v2.get", methods=["GET"])
def get(context, request, portal_type=None, uid=None):
    """
    """
    return {}
