# -*- coding: utf-8 -*-

from zope import interface

from DateTime import DateTime
from AccessControl import Unauthorized
from Products.Archetypes.utils import mapply

from bika.lims import logger
from bika.lims.jsonapi import api
from bika.lims.jsonapi import underscore as _
from bika.lims.jsonapi.interfaces import IFieldManager


class ATFieldManager(object):
    """Adapter to get/set the value of AT Fields
    """
    interface.implements(IFieldManager)

    def __init__(self, field):
        self.field = field
        self.name = field.getName()

    def get_field(self):
        """Get the adapted field
        """
        return self.field

    def get(self, instance, **kw):
        """Get the value of the field
        """
        return self._get(instance, **kw)

    def set(self, instance, value, **kw):
        """Set the value of the field
        """
        return self._set(instance, value, **kw)

    def _set(self, instance, value, **kw):
        """Set the value of the field
        """
        logger.debug("ATFieldManager::set: value=%r" % value)

        # check field permission
        if not self.field.checkPermission("write", instance):
            raise Unauthorized("You are not allowed to write the field {}"
                               .format(self.name))

        # check if field is writable
        if not self.field.writeable(instance):
            raise Unauthorized("Field {} is read only."
                               .format(self.name))

        # id fields take only strings
        if self.name == "id":
            value = str(value)

        # get the field mutator
        mutator = self.field.getMutator(instance)

        # Inspect function and apply *args and **kwargs if possible.
        mapply(mutator, value, **kw)

        return True

    def _get(self, instance, **kw):
        """Get the value of the field
        """
        logger.debug("ATFieldManager::get: instance={} field={}"
                     .format(instance, self.field))

        # check the field permission
        if not self.field.checkPermission("read", instance):
            raise Unauthorized("You are not allowed to read the field {}"
                               .format(self.name))

        # return the field value
        return self.field.get(instance)


class TextFieldManager(ATFieldManager):
    """Adapter to get/set the value of Text Fields
    """
    interface.implements(IFieldManager)


class DateTimeFieldManager(ATFieldManager):
    """Adapter to get/set the value of DateTime Fields
    """
    interface.implements(IFieldManager)

    def set(self, instance, value, **kw):
        """Converts the value into a DateTime object before setting.
        """
        try:
            value = DateTime(value)
        except SyntaxError:
            logger.warn("Value '{}' is not a valid DateTime string"
                        .format(value))
            return False

        self._set(instance, value, **kw)


class FileFieldManager(ATFieldManager):
    """Adapter to get/set the value of File Fields
    """
    interface.implements(IFieldManager)

    def set(self, instance, value, **kw):
        """Decodes base64 value and set the file object
        """
        value = str(value).decode("base64")

        # handle the filename
        if "filename" not in kw:
            logger.debug("FielFieldManager::set: No Filename detected "
                         "-> using title or id")
            kw["filename"] = kw.get("id") or kw.get("title")

        self._set(instance, value, **kw)


class ProxyFieldManager(ATFieldManager):
    """Adapter to get/set the value of Proxy Fields
    """
    interface.implements(IFieldManager)

    def __init__(self, field):
        super(ProxyFieldManager, self).__init__(field)
        self.proxy_object = None
        self.proxy_field = None

    def get_proxy_object(self, instance):
        """Get the proxy object of the field
        """
        return self.field._get_proxy(instance)

    def get_proxy_field(self, instance):
        """Get the proxied field of this field
        """
        proxy_object = self.get_proxy_object(instance)
        if not proxy_object:
            return None
        return proxy_object.getField(self.name)

    def set(self, instance, value, **kw):
        """Set the value of the (proxy) field
        """
        proxy_field = self.get_proxy_field(instance)
        if proxy_field is None:
            return None
        # set the field with the proper field manager of the proxy field
        fieldmanager = IFieldManager(proxy_field)
        return fieldmanager.set(instance, value, **kw)


class ReferenceFieldManager(ATFieldManager):
    """Adapter to get/set the value of Reference Fields
    """
    interface.implements(IFieldManager)

    def __init__(self, field):
        super(ReferenceFieldManager, self).__init__(field)
        self.allowed_types = field.allowed_types
        self.multi_valued = field.multiValued

    def is_multi_valued(self):
        return self.multi_valued

    def set(self, instance, value, **kw):
        """Set the value of the refernce field
        """
        ref = []

        # The value is an UID
        if api.is_uid(value):
            ref.append(api.get_object_by_uid(value))

        # The value is already an object
        if api.is_at_content(value):
            ref.append(value)

        # The value is a dictionary
        # -> handle it like a catalog query
        if _.is_dict(value):
            results = api.search(portal_type=self.allowed_types, **value)
            ref = map(api.get_object, results)

        # The value is a list
        if _.is_list(value):
            for item in value:
                # uid
                if api.is_uid(item):
                    ref.append(api.get_object_by_uid(item))
                    continue

                # object
                if api.is_at_content(item):
                    ref.append(api.get_object(item))
                    continue

                # path
                if api.is_path(item):
                    ref.append(api.get_object_by_path(item))
                    continue

                # dict (catalog query)
                if _.is_dict(item):
                    results = api.search(portal_type=self.allowed_types, **item)
                    objs = map(api.get_object, results)
                    ref.extend(objs)
                    continue

                # Plain string
                # -> do a catalog query for title
                if isinstance(item, basestring):
                    results = api.search(portal_type=self.allowed_types, title=item)
                    objs = map(api.get_object, results)
                    ref.extend(objs)
                    continue

        # The value is a physical path
        if api.is_path(value):
            ref = api.get_object_by_path(value)

        # Handle non multi valued fields
        if not self.multi_valued and len(ref) > 1:
            raise ValueError("Multiple values given for single valued field {}"
                             .format(self.field))

        return self._set(instance, ref, **kw)
