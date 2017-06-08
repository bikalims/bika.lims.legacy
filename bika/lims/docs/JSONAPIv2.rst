JSON API v2
===========

Running this test from the buildout directory::

    bin/test test_textual_doctests -t JSONAPIv2


Test Setup
----------

Needed Imports::

    >>> import transaction

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

    >>> from bika.lims import api

Functional Helpers::

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def login(user=TEST_USER_ID, password=TEST_USER_PASSWORD):
    ...     browser.open(portal_url + "/login_form")
    ...     browser.getControl(name='__ac_name').value = user
    ...     browser.getControl(name='__ac_password').value = password
    ...     browser.getControl(name='submit').click()
    ...     assert("__ac_password" not in browser.contents)

    >>> def logout():
    ...     browser.open(portal_url + "/logout")
    ...     assert("You are now logged out" in browser.contents)

Variables::

    >>> portal = self.getPortal()
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> bika_setup_url = portal_url + "/bika_setup"
    >>> browser = self.getBrowser()

JSON API::

    >>> api_base_url = portal_url + "/@@API/v2"


Version
=======

Ensure we are logged out::

    >>> logout()

The version route should be visible to unauthenticated users::

    >>> browser.open(api_base_url + "/version")
    >>> browser.contents
    '{"url": "http://nohost/plone/@@API/v2/version", "date": "...", "version": ..., "_runtime": ...}'
