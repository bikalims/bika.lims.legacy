==========
CientTypes
==========

Certain client require licences to operater. So a licences can be stored in the client
based of the client type

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ClientTypes

Test Setup
==========
Needed Imports::

    >>> import transaction
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest

    >>> def create(container, portal_type, title=None):
    ...     # Creates a content in a container and manually calls processForm
    ...     title = title is None and "Test {}".format(portal_type) or title
    ...     _ = container.invokeFactory(portal_type, id="tmpID", title=title)
    ...     obj = container.get(_)
    ...     obj.processForm()
    ...     modified(obj)  # notify explicitly for the test
    ...     transaction.commit()  # somehow the created method did not appear until I added this
    ...     return obj


Variables::

    >>> portal = self.portal
    >>> bika_setup = portal.bika_setup
    >>> clienttypes = bika_setup.bika_clienttypes
    >>> portal_url = portal.absolute_url()
    >>> browser = self.getBrowser()
    >>> current_user = ploneapi.user.get_current()
    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Manager'])
    >>> transaction.commit()



ClientType
==========

A `ClientType` lives in `ClientTypes` folder::

    >>> clienttype = ploneapi.content.create(clienttypes, "ClientType", title="Cultivator")
    >>> clienttype
    <ClientType at /plone/bika_setup/bika_clienttypes/cultivator>


Client
======

A `client` lives in the `/clients` folder::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> transaction.commit()
    >>> client
    <Client at /plone/clients/client-1>
    >>> client.setLicenses([{'Authority': 'AA', 'LicenseType':clienttype.UID(), 'LicenseID': 'MY ID', 'LicenseNumber': 'RS451'},])
    >>> transaction.commit()
    >>> client_url = client.absolute_url() + '/base_edit'
    >>> browser.open(client_url)
    >>> "edit_form" in browser.contents
    True
    >>> browser.getControl(name='Licenses.LicenseID:records', index=0).value == 'MY ID'
    True
    >>> browser.getControl(name='Licenses.LicenseType:records', index=0).value[0] == clienttype.UID()
    True
