import os

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.component import getAdapters
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from pkg_resources import resource_listdir, resource_exists

from bika.lims.interfaces import ISetupDataSetList


class SetupDataSetList:
    implements(ISetupDataSetList)

    def __init__(self, context):
        self.context = context

    def __call__(self, projectname="bika.lims"):
        datasets = []
        for fn in resource_listdir(projectname, 'setupdata'):
            fn += ".zip"
            if resource_exists(projectname, 'setupdata/%s' % fn):
                datasets.append({"projectname": projectname, "dataset": fn})
        return datasets


class SetupDataView(BrowserView):
    implements(IFolderContentsView, IViewView)
    template = ViewPageTemplateFile('templates/bika_setupdata.pt')

    def __init__(self, context, request):
        super(SetupDataView, self).__init__(context, request)

    def __call__(self):
        self.datasets = self.getSetupDatas()
        return self.template()

    def getSetupDatas(self):
        """Return a list of built-in datasets from all adapters which provide
        ISetupDataSetList
        """
        datasets = []
        # The ISetupDataSetList adapters are registered against IPloneSiteRoot.
        adapters = getAdapters((self.context.aq_parent,), ISetupDataSetList)
        for name, adapter in adapters:
            datasets.extend(adapter())
        return datasets


class ImportLimsData(BrowserView):
    template = ViewPageTemplateFile('templates/import-lims-data.pt')

    def __init__(self, context, request):
        super(ImportLimsData, self).__init__(context, request)

    def __call__(self):
        import pdb;
        pdb.set_trace()
        return self.template()
