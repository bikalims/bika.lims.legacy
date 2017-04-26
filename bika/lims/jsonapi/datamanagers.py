# -*- coding: utf-8 -*-

from zope import interface

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore import permissions

from bika.lims.jsonapi.exceptions import APIError
from bika.lims.jsonapi.interfaces import IDataManager
from bika.lims.jsonapi.interfaces import IFieldManager
from bika.lims import logger


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

        # bail out if we have no field
        if not field:
            return None

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.set(self.context, value, **kw)

    def get(self, name, **kw):
        """Get the value of the field by name
        """
        logger.debug("ATDataManager::get: fieldname=%s", name)

        # fetch the field by name
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return None

        # call the field adapter and get the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.get(self.context, **kw)
