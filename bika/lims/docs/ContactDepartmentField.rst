Setup Data
==========

Client Contact has a new field called Department and the value of the field
comes from the class Client Department whose parent is Client Departments.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ContactDepartmentField


Test Setup
----------

Needed Imports::

    >>> import transaction
    >>> from bika.lims import api

    >>> def create(container, portal_type, title=None):
    ...     obj = api.create(container, portal_type, title=title)
    ...     # doctest fixture to make the content visible for the test browser
    ...     transaction.commit()  # somehow the created method did not appear until I added this
    ...     return obj


Variables::

    >>> portal = self.portal
    >>> bika_setup = portal.bika_setup
    >>> clientdepartments = bika_setup.bika_clientdepartments
    >>> portal_url = portal.absolute_url()
    >>> browser = self.getBrowser()


ClientDepartment
----------------

A `ClientDepartment` lives in `ClientDepartments` folder::

    >>> clientdepartment = create(clientdepartments, "ClientDepartment", title="Test Department")
    >>> clientdepartment
    <ClientDepartment at /plone/bika_setup/bika_clientdepartments/clientdepartment-1>


Client
======

A `client` lives in the `/clients` folder::

    >>> clients = portal.clients
    >>> client1 = create(clients, "Client", title="Client-1")
    >>> client_contact_url = client1.absolute_url() + '/contacts'
    >>> browser.open(client_contact_url)
    >>> browser.getLink('Add').click()
    >>> browser.getControl('Firstname').value = 'Test'
    >>> browser.getControl('Surname').value = 'Contact'
    >>> browser.getControl('Test Department').selected = True
    >>> browser.getControl(name='form.button.save').click()
    >>> 'Changes saved' and 'Test Department' in browser.contents
    True
    >>> browser.getControl('Test Department')
    <ItemControl name='Department' type='select' optionValue='clientdepartment-1' selected=True>
