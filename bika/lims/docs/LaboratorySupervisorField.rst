Setup Data
==========

Lab Information(Laboratory or Organisation) has a new field called
LaboratorySupervisor and the value of the field comes from the class
Lab Contact whose parent is Lab Contacts.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t LaboratorySupervisorField


Test Setup
----------

Needed Imports::

    >>> import transaction
    >>> from plone import api as ploneapi
    >>> from bika.lims import api
    >>> current_user = ploneapi.user.get_current()
    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Manager'])
    >>> transaction.commit()


Variables::

    >>> portal = self.portal
    >>> bika_setup = portal.bika_setup
    >>> labcontacts = bika_setup.bika_labcontacts
    >>> portal_url = portal.absolute_url()
    >>> browser = self.getBrowser()


Lab Contact
===========

A `labcontact` lives in the `/bika_labcontacts` folder::

    >>> labcontact = api.create(labcontacts, "LabContact", Firstname="MyFirstName", Surname="MySurname")
    >>> transaction.commit()
    >>> labcontact
    <LabContact at /plone/bika_setup/bika_labcontacts/labcontact-1>


Lab Information
===============

`laboratory aka laboratory information` is found under `/bika_setup`::

    >>> laboratory = bika_setup.laboratory
    >>> laboratory_info_url = laboratory.absolute_url() + '/base_edit'
    >>> browser.open(laboratory_info_url)
    >>> browser.getControl('MyFirstName MySurname').selected = True
    >>> browser.getControl(name='form.button.save').click()
    >>> 'Changes saved' and 'MyFirstName MySurname' in browser.contents
    True
    >>> browser.getControl('MyFirstName MySurname')
    <ItemControl name='LaboratorySupervisor' type='select' optionValue='labcontact-1' selected=True>
