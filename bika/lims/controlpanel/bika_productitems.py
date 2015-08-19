from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.lims.interfaces import IProductItems

from bika.lims.browser.bika_listing import WorkflowAction
import plone
import time
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import doActionFor
from bika.lims.utils import t
from bika.lims import PMF

class ProductItemsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ProductItemsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'ProductItem',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=ProductItem',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Product Items"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/product_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.filter_indexes.append('getBatchId')
        self.columns = {
            'productItemID': {'title': _('Product Item ID'),
                      'index': 'sortable_title',
                      'toggle': True},
            'orderId': {'title': _('Order Id'),
                       'toggle': True},
            'labId': {'title': _('Lab Id'),
                       'toggle': False},
            'batchId': {'title': _('Batch Id'),
                       'index' : 'getBatchId',
                       'toggle': True},
            'product': {'title': _('Product'),
                       'toggle': True},
            'supplier': {'title': _('Supplier'),
                       'toggle': True},
            'productCategory': {'title': _('Category'),
                       'toggle': True},
            'location': {'title': _('Location'),
                       'toggle': False},
            'dateReceived': {'title': _('Date Received'),
                       'toggle': True},
            'dateOpened': {'title': _('Date Opened'),
                       'toggle': True},
            'expiryDate': {'title': _('Expiry Date'),
                       'toggle': False},
            'disposalDate': {'title': _('Disposal Date'),
                       'toggle': False},
            'storageLevelId': {'title': _('Storage Level ID'),
                       'toggle': False},
            'isStored': {'title': _('Is Stored'),
                       'toggle': False},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Valid'),
             'contentFilter': {'review_state': 'valid'},
             'transitions': [{'id':'discard'}, ],
             'columns': ['productItemID',
                         'orderId',
                         'labId',
                         'batchId',
                         'product',
                         'supplier',
                         'productCategory',
                         'location',
                         'storageLevelId',
                         'isStored',
                         'dateReceived',
                         'dateOpened',
                         'expiryDate',
                         'disposalDate']},
            {'id':'discarded',
             'title': _('Discarded'),
             'contentFilter': {'review_state': 'discarded'},
             'transitions': [{'id':'keep'}, ],
             'columns': ['productItemID',
                         'orderId',
                         'labId',
                         'batchId',
                         'product',
                         'supplier',
                         'productCategory',
                         'location',
                         'storageLevelId',
                         'isStored',
                         'dateReceived',
                         'dateOpened',
                         'expiryDate',
                         'disposalDate']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['productItemID',
                         'orderId',
                         'labId',
                         'batchId',
                         'product',
                         'Supplier',
                         'ProductCategory',
                         'location',
                         'storageLevelId',
                         'isStored',
                         'dateReceived',
                         'dateOpened',
                         'expiryDate',
                         'disposalDate']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['orderId'] = obj.getOrderId()
            items[x]['labId'] = obj.getLabId()
            items[x]['batchId'] = obj.getBatchId()
            items[x]['product'] = obj.getProductTitle()
            items[x]['supplier'] = obj.getSupplierTitle()
            items[x]['productCategory'] = obj.getProductCategoryTitle()
            items[x]['location'] = obj.getLocation()
            items[x]['storageLevelId'] = obj.getStorageLevelID()
            items[x]['isStored'] = 'yes' if obj.getIsStored() else 'no'
            items[x]['dateReceived'] = self.ulocalized_time(obj.getDateReceived())
            items[x]['dateOpened'] = self.ulocalized_time(obj.getDateOpened())
            items[x]['expiryDate'] = self.ulocalized_time(obj.getExpiryDate())
            items[x]['disposalDate'] = self.ulocalized_time(obj.getDisposalDate())
            items[x]['replace']['productItemID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], obj.getProductItemId())
        return items

schema = ATFolderSchema.copy()
class ProductItems(ATFolder):
    implements(IProductItems)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ProductItems, PROJECTNAME)

class ProductItemsWorkflowAction(WorkflowAction):

    """Workflow actions taken in ProductItems context.

    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]
        if type(came_from) in (list, tuple):
            came_from = came_from[0]
        # Call out to the workflow action method
        # Use default bika_listing.py/WorkflowAction for other transitions
        method_name = 'workflow_action_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_discard(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        objects = WorkflowAction._get_selected_items(self)
        for obj_uid, obj in objects.items():
            pitem = obj
            old_d = pitem.Description()
            new_message = "\n*** Discarded at " + time.strftime("%c") + " ***\n"
            pitem.setDescription(old_d + new_message)
            pitem.reindexObject()
            workflow.doActionFor(pitem, action)
        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)

    def workflow_action_keep(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        objects = WorkflowAction._get_selected_items(self)
        for obj_uid, obj in objects.items():
            pitem = obj
            old_d = pitem.Description()
            new_message = "\n*** Restored in Inventory at " + time.strftime("%c") + " ***\n"
            pitem.setDescription(old_d + new_message)
            pitem.reindexObject()
            workflow.doActionFor(pitem, action)
        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)
