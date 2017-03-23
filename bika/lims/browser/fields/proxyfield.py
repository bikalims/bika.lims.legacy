# -*- coding: utf-8 -*-

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField

from bika.lims.interfaces import IProxyField

"""A field that proxies to an object which is retrieved by the evaluation of
the `proxy` property, e.g. `proxy="context.getSample()"`.

See `docs/AnalysisRequest.rst` for further details.
"""


class ProxyField(ObjectField):
    """A field that proxies to another field of an object, which is retrieved
    by the `proxy` expression property.
    """
    implements(IProxyField)

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'proxy',
        'mode': 'rw',
        'default': None,
        'proxy': None,
    })

    security = ClassSecurityInfo()

    def _get_proxy(self, instance):
        """Evaluate the `proxy` property to retrieve the proxy object.
        """
        return eval(self.proxy, {'context': instance, 'here': instance})

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """retrieves the value of the same named field on the proxy object
        """
        # Retrieve the proxy object
        proxy = self._get_proxy(instance)

        # Bail out if we do not find a proxy object
        if proxy is None:
            return None

        # Lookup the proxied field by name
        field_name = self.getName()
        field = proxy.getField(field_name)

        # Bail out it the proxy object has no identical named field
        if not field:
            raise KeyError("Expression '{}' did not return a valid Proxy Object on {}"
                           .format(self.proxy, self.instance))

        # return the value of the proxy field
        return field.get(proxy)

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """writes the value to the same named field on the proxy object
        """
        # Retrieve the proxy object
        proxy = self._get_proxy(instance)

        # Bail out if we do not find a proxy object
        if not proxy:
            raise KeyError("Expression '{}' did not return a valid Proxy Object on {}"
                           .format(self.proxy, self.instance))

        # Lookup the proxied field by name
        field_name = self.getName()
        field = proxy.getField(field_name)

        # Bail out it the proxy object has no identical named field.
        if field is None:
            raise KeyError("Object '{}' has no field named '{}'".format(
                proxy.portal_type, field_name))

        # set the value on the proxy object
        field.set(proxy, value, **kwargs)


# Register the field
registerField(
    ProxyField,
    title='Proxy',
    description=('Used to proxy a value to an underlying object.')
)
