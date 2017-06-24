Setup Data
==========

Client Contact has a new field called Department and the value of the field
comes from the class Client Department whose parent is Client Departments.
Please note that Client Department is a Dexterity class, hence the use of 
ploneapi to create the the object.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ContactDepartmentField


Test Setup
----------

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
    >>> clientdepartments = bika_setup.bika_clientdepartments
    >>> portal_url = portal.absolute_url()
    >>> browser = self.getBrowser()


ClientDepartment
----------------

A `ClientDepartment` lives in `ClientDepartments` folder::

    >>> clientdepartment = ploneapi.content.create(clientdepartments, "ClientDepartment", title="Test Department")
    >>> clientdepartment
    <ClientDepartment at /plone/bika_setup/bika_clientdepartments/test-department>

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
    <ItemControl name='Department' type='select' optionValue='test-department' selected=True>
