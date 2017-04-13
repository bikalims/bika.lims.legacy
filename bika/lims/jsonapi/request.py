# -*- coding: utf-8 -*-

import json
import pkg_resources

from zope import interface

from zope.globalrequest import getRequest

try:
    pkg_resources.get_distribution('plone.protect')
    from plone.protect.interfaces import IDisableCSRFProtection
except (pkg_resources.DistributionNotFound, ImportError):
    HAS_PLONE_PROTECT = False
else:
    HAS_PLONE_PROTECT = True

from bika.lims import logger
from bika.lims.jsonapi import underscore as _


# These values evaluate to True
TRUE_VALUES = ["y", "yes", "1", "true", True]


def get_request():
    """Get the current request

    >>> get_request()
    <HTTPRequest, URL=http://nohost>
    """
    return getRequest()


def disable_csrf_protection():
    """ disables the CSRF protection
        https://pypi.python.org/pypi/plone.protect
    """
    if not HAS_PLONE_PROTECT:
        logger.warn(
            "Can not disable CSRF protection – please install plone.protect"
        )
        return False
    request = get_request()
    interface.alsoProvides(request, IDisableCSRFProtection)
    return True


def get_form():
    """Get the request form dictionary

    >>> get_form()
    {}
    """
    return get_request().form


def get(key, default=None):
    """Get the value for the given key from the request

    >>> get("limit", 0)
    0
    """
    return get_form().get(key, default)


def is_true(key, default=False):
    """Check if the value is in TRUE_VALUES

    >>> request = get_request()

    >>> out = []
    >>> for tv in TRUE_VALUES:
    ...     request.form["param"] = tv
    ...     out.append(is_true("param"))
    >>> all(out)
    True
    """
    value = get(key, default)
    if isinstance(value, list):
        value = value[0]
    if isinstance(value, bool):
        return value
    if value is default:
        return default
    return value.lower() in TRUE_VALUES


def get_cookie(key, default=None):
    """Get the cookie by key
    """
    return get_request().cookies.get(key, default)


def get_complete(default=None):
    """Get the 'complete' value from the request

    >>> request = get_request()
    >>> request.form["complete"] = "yes"
    >>> get_complete()
    True
    """
    return is_true("complete", default)


def get_children(default=None):
    """Get the 'children' value from the request

    >>> request = get_request()
    >>> request.form["children"] = "yes"
    >>> get_children()
    True
    """
    return is_true("children", default)


def get_filedata(default=None):
    """Get the 'filedata' value from the request

    >>> request = get_request()
    >>> request.form["filedata"] = "yes"
    >>> get_filedata()
    True
    """
    return is_true('filedata')


def get_workflow(default=None):
    """Get the 'workflow' value from the request

    >>> request = get_request()
    >>> request.form["workflow"] = "yes"
    >>> get_workflow()
    True
    """
    return is_true("workflow", default)


def get_sharing(default=None):
    """Get the 'sharing' value from the request

    >>> request = get_request()
    >>> request.form["sharing"] = "yes"
    >>> get_sharing()
    True
    """
    return is_true("sharing", default)


def get_sort_limit():
    """Get the 'sort_limit' value from the request
    """
    limit = _.convert(get("sort_limit"), _.to_int)
    if (limit < 1):
        limit = None  # catalog raises IndexError if limit < 1
    return limit


def get_batch_size():
    """Get the 'limit' value from the request
    """
    return _.convert(get("limit"), _.to_int) or 25


def get_batch_start():
    """Get the 'b_start' value from the request
    """
    return _.convert(get("b_start"), _.to_int) or 0


def get_sort_on(allowed_indexes=None):
    """Get the 'sort_on' value from the request
    """
    sort_on = get("sort_on", "getObjPositionInParent")
    if allowed_indexes and sort_on not in allowed_indexes:
        logger.warn("Index '%s' is not in allowed_indexes" % sort_on)
        return "id"
    return sort_on


def get_sort_order():
    """Get the 'sort_order' value from the request
    """
    sort_order = get("sort_order")
    if sort_order in ["ASC", "ascending", "a", "asc", "up", "high"]:
        return "ascending"
    if sort_order in ["DESC", "descending", "d", "desc", "down", "low"]:
        return "descending"
    # https://github.com/collective/plone.jsonapi.routes/issues/31
    return "ascending"


def get_query():
    """Get the 'query' from the request
    """
    q = get("q", "")

    qs = q.lstrip("*.!$%&/()=#-+:'`´^")
    if qs and not qs.endswith("*"):
        qs += "*"
    return qs


def get_path():
    """Get the 'path' value from the request
    """
    return get("path", "")


def get_depth():
    """Get the 'depth' value from the request
    """
    return _.convert(get("depth", 0), _.to_int)


def get_recent_created():
    """Get the 'recent_created' value from the request
    """
    return get("recent_created", None)


def get_recent_modified():
    """Get the 'recent_modified' value from the request
    """
    return get("recent_modified", None)


def get_request_data():
    """Extract and convert the json data from the request

    >>> get_request_data()
    [{}]

    :returns: A list of dictionaries
    :rtype: list
    """
    request = get_request()
    data = request.get("BODY", "{}")
    if not is_json_deserializable(data):
        from plone.jsonapi.routes.exceptions import APIError
        raise APIError(400, "Request Data is not JSON deserializable – Check JSON Syntax!")
    return _.convert(json.loads(data), _.to_list)


def get_json():
    """Get the request json payload

    >>> get_json()
    {}
    """
    data = get_request_data().pop()
    return data or dict()


def get_json_key(key, default=None):
    """Get the key from the json payload

    >>> set_json_item("test", True)
    >>> get_json_key("test")
    True
    """
    return get_json().get(key, default)


def set_json_item(key, value):
    """Manipulate JSON data on the fly

    >>> set_json_item("name", "test")
    >>> get_json_key("name")
    u'test'
    """
    data = get_json()
    data[key] = value

    request = get_request()
    request["BODY"] = json.dumps(data)


def is_json_deserializable(thing):
    """Checks if the given thing can be deserialized from JSON

    >>> is_json_deserializable("{}")
    True
    >>> is_json_deserializable("[]")
    True
    >>> is_json_deserializable("<>")
    False

    :param thing: The object to check if it can be serialized
    :type thing: arbitrary object
    :returns: True if it can be JSON deserialized
    :rtype: bool
    """
    try:
        json.loads(thing)
        return True
    except (ValueError):
        return False
