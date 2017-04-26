# -*- coding: utf-8 -*-

from zope import interface
from zope.schema import getFields
from zope.schema.interfaces import IObject

from plone import api as ploneapi
from plone.behavior.interfaces import IBehaviorAssignable

from DateTime import DateTime
from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore import permissions
from Products.Archetypes.utils import mapply
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import DateTimeField

from bika.lims.jsonapi import api
from bika.lims.jsonapi import underscore as _
from bika.lims.jsonapi.exceptions import APIError
from bika.lims.jsonapi.interfaces import IDataManager
from bika.lims import logger
from bika.lims.browser.fields import ProxyField

import pkg_resources
try:
    pkg_resources.get_distribution('plone.app.textfield')
    from plone.app.textfield.interfaces import IRichText
    from plone.app.textfield.value import RichTextValue
except (pkg_resources.DistributionNotFound, ImportError):
    HAS_PLONE_APP_TEXTFIELD = False
else:
    HAS_PLONE_APP_TEXTFIELD = True


class BrainDataManager(object):
    """Adapter to get catalog brain attributes
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get(self, name):
        """Get the value by name
        """
        # read the attribute
        attr = getattr(self.context, name, None)
        if callable(attr):
            return attr()
        return attr

    def set(self, name, value, **kw):
        """Not used for catalog brains
        """
        logger.warn("set attributes not allowed on catalog brains")


class PortalDataManager(object):
    """Adapter to set and get attributes of the Plone portal
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get(self, name):
        """Get the value by name
        """

        # check read permission
        sm = getSecurityManager()
        permission = permissions.View
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to view the Plone portal")

        # read the attribute
        attr = getattr(self.context, name, None)
        if callable(attr):
            return attr()

        # XXX no really nice, but we want the portal to behave like an ordinary
        # content type. Therefore we need to inject the neccessary data.
        if name == "uid":
            return 0
        if name == "path":
            return "/%s" % self.context.getId()
        return attr

    def set(self, name, value, **kw):
        """Set the attribute to the given value.

        The keyword arguments represent the other attribute values
        to integrate constraints to other values.
        """

        # check write permission
        sm = getSecurityManager()
        permission = permissions.ManagePortal
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to modify the Plone portal")

        # set the attribute
        if not hasattr(self.context, name):
            return False
        self.context[name] = value
        return True


class ATDataManager(object):
    """Adapter to set and get field values of AT Content Types
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get_schema(self):
        """Get the schema
        """
        try:
            return self.context.Schema()
        except AttributeError:
            raise APIError(400, "Can not get Schema of %r" % self.context)

    def is_file_field(self, field):
        """Checks if field is a file field
        """
        # XXX find a better way to distinguish file/image fields
        if getattr(field, "type", None) in ["file", "image", "blob"]:
            return True
        return False

    def is_reference_field(self, field):
        """Checks if the field is a reference field
        """
        return isinstance(field, ReferenceField)

    def is_datetime_field(self, field):
        """Checks if the field is a datetime field
        """
        return isinstance(field, DateTimeField)

    def is_proxy_field(self, field):
        """Checks if the field is a datetime field
        """
        return isinstance(field, ProxyField)

    def get_field(self, name):
        """Get the field by name
        """
        field = self.context.getField(name)
        return field

    def set(self, name, value, **kw):
        """Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """

        # fetch the field by name
        field = self.get_field(name)

        # Handle Proxy fields to get the right field type below
        if self.is_proxy_field(field):
            proxy_object = field._get_proxy(self.context)
            if proxy_object:
                field = proxy_object.getField(name)

        # bail out if we have no field
        if not field:
            return False

        # check the field permission
        if not field.checkPermission("write", self.context):
            raise Unauthorized("Not allowed to write the field %s" % name)

        # Handle DateTime Fields
        if self.is_datetime_field(field):
            try:
                value = DateTime(value)
            except SyntaxError:
                logger.warn("Value '{}' is not a valid DateTime string"
                            .format(value))
                return False

        # Handle File Fields
        if self.is_file_field(field):
            logger.debug("ATDataManager::set:File field detected ('%r'), "
                         "base64 decoding value", field)
            value = str(value).decode("base64")
            # handle the filename
            if "filename" not in kw:
                logger.debug("ATDataManager::set: No Filename detected "
                             "-> using title or id")
                kw["filename"] = kw.get("id") or kw.get("title")

        # Handle Reference Fields
        if self.is_reference_field(field):
            logger.debug("ATDataManager::set:Reference Field detected -> ('%r')", field)

            # Allowed objects to set as a reference
            allowed_types = field.allowed_types

            # The new reference
            new_reference = None

            # The value is already an object
            if api.is_at_content(value):
                new_reference = value

            # Value is an UID
            if api.is_uid(value):
                new_reference = api.get_object_by_uid(value)

            # Value is a dictionary
            # => handle it like a catalog query
            if _.is_dict(value):
                results = api.search(portal_type=allowed_types, **value)
                if len(results) == 1:
                    new_reference = api.get_object(results[0])
                if len(results) == 0:
                    logger.warn("No reference of type(s) '{}' found for the query '{}'"
                                .format(allowed_types, value))
                    return False
                if len(results) > 1:
                    logger.warn("Multiple references of type(s) '{}' found by the query '{}'"
                                .format(allowed_types, value))
                    return False
            # Value is a path
            if api.is_path(value):
                new_reference = api.get_object_by_path(value)

            # No object found but we have a value
            if not new_reference and value:
                # query for an id
                results = api.search(portal_type=allowed_types, title=value)
                if len(results) == 1:
                    new_reference = api.get_object(results[0])

            # No reference found
            if not new_reference:
                logger.warn("No objects of type(s) '{}' found for the value '{}'"
                            .format(allowed_types, value))
                return False

            portal_type = api.get_portal_type(new_reference)
            if portal_type not in allowed_types:
                logger.warn("Portal type '{}' is not in the list of allowed types for this field '{}'"
                            .format(portal_type, allowed_types))
                return False

            value = new_reference

        # id fields take only strings
        if name == "id":
            value = str(value)

        # set the value to the field
        self._set(field, value, **kw)

        return True

    def _set(self, field, value, **kw):
        """Set the raw value of the field
        """
        logger.debug("ATDataManager::set: field=%r, value=%r", field, value)
        # get the field mutator
        mutator = field.getMutator(self.context)
        # Inspect function and apply positional and keyword arguments if
        # possible.
        return mapply(mutator, value, **kw)

    def get(self, name):
        """Get the value of the field by name
        """

        # fetch the field by name
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return None

        # check the field permission
        if not field.checkPermission("read", self.context):
            raise Unauthorized("Not allowed to read the field %s" % name)

        # return the field value
        return field.get(self.context)


class DexterityDataManager(object):
    """Adapter to set and get field values of Dexterity Content Types
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context
        self.schema = self.get_schema()
        self.behaviors = self.get_behaviors()

    def get_behaviors(self):
        """Iterate over all behaviors that are assigned to the object
        Used code from @tisto:
        https://github.com/plone/plone.restapi/blob/master/src/plone/restapi/utils.py
        """
        out = {}
        assignable = IBehaviorAssignable(self.context, None)
        if not assignable:
            return out
        for behavior in assignable.enumerateBehaviors():
            for name, field in getFields(behavior.interface).items():
                out[name] = field
        return out

    def get_schema(self):
        pt = ploneapi.portal.get_tool("portal_types")
        fti = pt.getTypeInfo(self.context.portal_type)
        return fti.lookupSchema()

    def get_field(self, name):
        sf = self.schema.get(name)
        bf = self.behaviors.get(name)
        return sf or bf

    def is_file_field(self, field):
        """Checks if field is a file field
        """
        if _.is_string(field):
            field = self.get_field(field)
        if self.is_richtext_field(field):
            return False
        return IObject.providedBy(field)

    def is_richtext_field(self, field):
        """Checks if field is a rich-text field
        """
        if _.is_string(field):
            field = self.get_field(field)
        if HAS_PLONE_APP_TEXTFIELD:
            return IRichText.providedBy(field)
        return False

    def get_filename(self, **kw):
        """ extract the filename from the keywords
        """
        if "filename" not in kw:
            logger.debug("ATDataManager::get_filename:No Filename detected"
                         "-- using title or id")
            kw["filename"] = kw.get("id") or kw.get("title")
        return kw.get("filename")

    def get_content_type(self, **kw):
        """Extract the mimetype from the keywords
        """
        if "mimetype" in kw:
            return kw.get("mimetype")
        if "content_type" in kw:
            # same key as in JSON response
            return kw.get("content_type")
        return None

    def can_write(self, field):
        """Checks if the field is writeable
        """
        # check if the field is read only
        if field.readonly:
            raise Unauthorized("Field '%s' is read-only" % field.__name__)

        # XXX: How to check security on the field level?
        sm = getSecurityManager()
        permission = permissions.ModifyPortalContent
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to modify this content")
        return field

    def can_read(self, field):
        """Checks if the field is readable
        """
        # XXX: How to check security on the field level?
        sm = getSecurityManager()
        if not sm.checkPermission(permissions.View, self.context):
            raise Unauthorized("Not allowed to view this content")
        return field

    def set(self, name, value, **kw):
        """Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return False

        # Check the write permission of the field
        self.can_write(field)

        if self.is_richtext_field(field):
            logger.debug("DexterityDataManager::set:RichText field"
                         "detected ('%r'), creating RichTextValue", field)
            value = RichTextValue(raw=value,
                                  outputMimeType=field.output_mime_type)

        if self.is_file_field(field):
            logger.debug("DexterityDataManager::set:File field"
                         "detected ('%r'), base64 decoding value", field)
            data = str(value).decode("base64")
            filename = self.get_filename(**kw)
            contentType = self.get_content_type(**kw)

            if contentType:
                # create NamedFile with content type information
                value = field._type(data=data, contentType=contentType,
                                    filename=filename)
            else:
                # create NamedFile w/o content type information
                # -> will be guessed by the extension of the filename
                value = field._type(data=data, filename=filename)

        # only possible with non file fields
        if not self.is_file_field(field):
            # validate the field value
            field.validate(value)

        logger.debug("DexterityDataManager::set:"
                     "field=%r, value=%r", field, value)

        field.set(self.context, value)
        return True

    def get(self, name):
        """Get the value of the field by name
        """
        field = self.get_field(name)
        if field is None:
            return None
        # Check the read permission of the field
        self.can_read(field)
        return field.get(self.context)
