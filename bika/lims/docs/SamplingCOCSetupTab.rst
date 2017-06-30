SamplingCOCSetupTab
===================

Sampling COC Setup tab is a tab on BIKA Setup and has a fields that manage
the filters on ARs listing view.


Running this test from the buildout directory::

    bin/test test_textual_doctests -t SamplingCOCSetupTab


Test Setup
----------


    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest

    >>> import transaction
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

    >>> portal = self.getPortal()
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> bika_setup_url = portal_url + "/bika_setup"
    >>> from bika.lims import api

Variables::

    >>> sample_date = DateTime(2017, 1, 31)
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_samplepoints = bika_setup.bika_samplepoints
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices
    >>> bika_labcontacts = bika_setup.bika_labcontacts
    >>> portal_url = portal.absolute_url()
    >>> bika_setup_url = portal_url + "/bika_setup"


Analysis Requests (AR)
----------------------

An `AnalysisRequest` can only be created inside a `Client`::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> client
    <Client at /plone/clients/client-1>

To create a new AR, a `Contact` is needed::

    >>> contact = api.create(client, "Contact", Firstname="Ramon", Surname="Bartl")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>

A `SampleType` defines how long the sample can be retained, the minimum volume
needed, if it is hazardous or not, the point where the sample was taken etc.::

    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

A `SamplePoint` defines the location, where a `Sample` was taken::

    >>> samplepoint = api.create(bika_samplepoints, "SamplePoint", title="Lake of Constance")
    >>> samplepoint
    <SamplePoint at /plone/bika_setup/bika_samplepoints/samplepoint-1>

An `AnalysisCategory` categorizes different `AnalysisServices`::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>

An `AnalysisService` defines a analysis service offered by the laboratory::

    >>> analysisservice = api.create(bika_analysisservices, "AnalysisService", title="PH", ShortTitle="ph", Category=analysiscategory, Keyword="PH")
    >>> analysisservice
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

An `AnalysisRequest` can be created::

    >>> values = {
    ...           'Client': client,
    ...           'Contact': contact,
    ...           'SamplingDate': sample_date,
    ...           'DateSampled': sample_date,
    ...           'SampleType': sampletype
    ...          }

    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> transaction.commit()
    >>> browser = self.getBrowser()
    >>> ars_url = portal_url + '/analysisrequests'
    >>> browser.open(ars_url)
    >>> 'To Be Sampled' and 'To Be Preserved' and 'Scheduled sampling' in browser.contents
    True
    >>> bika_setup.setSamplingWorkflowEnabled(True)
    >>> bika_setup.setScheduleSamplingEnabled(True)
    >>> bika_setup.setSamplePreservationEnabled(True)
    >>> transaction.commit()
    >>> browser.open(ars_url)
    >>> 'To Be Sampled' and 'To Be Preserved' and 'Scheduled sampling' not in browser.contents
    True
    >>> 'Analysis Requests' in browser.contents
    True


