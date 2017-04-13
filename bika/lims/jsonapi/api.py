# -*- coding: utf-8 -*-

from AccessControl import Unauthorized

from bika.lims import api
from bika.lims import logger
from bika.lims.jsonapi.exceptions import APIError
from bika.lims.jsonapi.interfaces import IDataManager
from bika.lims.jsonapi import underscore as _


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
