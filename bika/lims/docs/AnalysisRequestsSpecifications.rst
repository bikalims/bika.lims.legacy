Analysis Requests Specifications
================================

Analysis Requests in Bika LIMS describe an Analysis Order from a Client to the
Laboratory. Analysis Specifications can be enabled/disabled on the 
Bika Setup Analyses Tab on Enable Analysis Specifications field
When the Enable Analysis Specifications is enabled, each Analysis can have 
3 Types of Default Specification 
1. Analysis Request Specification
2. Sample Type Specifications (Lab)
3. Sample Type Specifications (Client)

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AnalysisRequestsSpecifications


Test Setup
----------

Needed Imports::

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest

Functional Helpers::

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_samplepoints = bika_setup.bika_samplepoints
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices
    >>> bika_labcontacts = bika_setup.bika_labcontacts
    >>> bika_storagelocations = bika_setup.bika_storagelocations
    >>> bika_samplingdeviations = bika_setup.bika_samplingdeviations
    >>> bika_sampleconditions = bika_setup.bika_sampleconditions
    >>> portal_url = portal.absolute_url()
    >>> bika_setup_url = portal_url + "/bika_setup"
    >>> browser = self.getBrowser()


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

Set, the `EnableAnalysisSpecifications` and test if it's on the add form::
Switch on::
    >>> bika_setup.setEnableARSpecs(True)
    >>> transaction.commit()
    >>> bika_setup.getEnableARSpecs()
    True
    >>> create_ar_url = client.absolute_url() + '/ar_add?ar_count=1'
    >>> browser.open(create_ar_url)
    >>> browser.contents.count('Analysis Specification')
    2

Switch off::
    >>> bika_setup.setEnableARSpecs(False)
    >>> transaction.commit()
    >>> bika_setup.getEnableARSpecs()
    False
    >>> create_ar_url = client.absolute_url() + '/ar_add?ar_count=1'
    >>> browser.open(create_ar_url)
    >>> browser.contents.count('Analysis Specification')
    1

Finally, the `AnalysisRequest` can be created::

    >>> values = {
    ...           'Client': client,
    ...           'Contact': contact,
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype
    ...          }

    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> transaction.commit()
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/water-0001-R01>
    >>> ar_url = ar.absolute_url() + '/base_view'
    >>> browser.open(ar_url)
    >>> browser.contents.count('Analysis Specification')
    2
    >>> bika_setup.setEnableARSpecs(True)
    >>> transaction.commit()
    >>> bika_setup.getEnableARSpecs()
    True
    >>> ar_url = ar.absolute_url() + '/base_view'
    >>> browser.open(ar_url)
    >>> browser.contents.count('Analysis Specification')
    3
