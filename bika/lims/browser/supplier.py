from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.controlpanel.bika_instruments import InstrumentsView
from bika.lims.controlpanel.bika_products import ProductsView
from bika.lims.browser.order.orderfolder import OrderFolderView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from plone.app.layout.globals.interfaces import IViewView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

class SupplierInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(SupplierInstrumentsView, self).__init__(context, request)

    def folderitems(self):
        items = InstrumentsView.folderitems(self)
        uidsup = self.context.UID()
        outitems = []
        for x in range(len(items)):
            obj = items[x].get('obj', None)
            if obj and hasattr(obj, 'getRawSupplier') \
               and obj.getRawSupplier() == uidsup:
                outitems.append(items[x])
        return outitems


class SupplierProductsView(ProductsView):

    def __init__(self, context, request):
        super(SupplierProductsView, self).__init__(context, request)
        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseProducts()
        if self.do_cats:
            self.pagesize = 0  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.category_index = 'getCategoryTitle'
            for rs in self.review_states:
                if 'columns' in rs and 'Category' in rs['columns']:
                    rs['columns'].remove('Category')

    def folderitems(self):
        items = ProductsView.folderitems(self)
        uidsup = self.context.UID()
        outitems = []
        for x in range(len(items)):
            obj = items[x].get('obj', None)
            if obj and hasattr(obj, 'getSupplierUID') \
               and obj.getSupplierUID() == uidsup:

                cat = obj.getCategoryTitle()
                if self.do_cats:
                    # category is for bika_listing to groups entries
                    items[x]['category'] = cat
                    if cat not in self.categories:
                        self.categories.append(cat)
                after_icons = ''
                if obj.getHazardous():
                    after_icons = ("<img src='++resource++bika.lims.images/"
                                   "hazardous.png' title='Hazardous'>")
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                     (items[x]['url'], items[x]['Title'], after_icons)
                outitems.append(items[x])
        return outitems


class ProductPathBarViewlet(ViewletBase):
    """Viewlet for overriding breadcrumbs in Product View"""

    index = ViewPageTemplateFile('templates/path_bar.pt')

    def update(self):
        super(ProductPathBarViewlet, self).update()
        self.is_rtl = self.portal_state.is_rtl()
        breadcrumbs = getMultiAdapter((self.context, self.request),
                                      name='breadcrumbs_view').breadcrumbs()
        breadcrumbs[2]['absolute_url'] += '/products'
        self.breadcrumbs = breadcrumbs

class SupplierOrdersView(OrderFolderView):
    implements(IViewView)

    def __init__(self, context, request):
        super(SupplierOrdersView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'Order',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse',
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'level': 0
            }
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=Order',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }

class ReferenceSamplesView(BikaListingView):

    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/referencesample_big.png"
        self.title = self.context.translate(_("Reference Samples"))
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample',
                              'sort_on': 'id',
                              'sort_order': 'reverse',
                              'path': {"query": "/".join(context.getPhysicalPath()),
                                       "level" : 0 }
                              }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=ReferenceSample',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = {
            'ID': {'title': _('ID')},
            'Title': {'title': _('Title')},
            'Manufacturer': {'title': _('Manufacturer'), 'toggle':True},
            'Definition': {'title': _('Reference Definition'), 'toggle':True},
            'DateSampled': {'title': _('Date Sampled'),
                            'index': 'getDateSampled',
                            'toggle':True},
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived',
                             'toggle':True},
            'DateOpened': {'title': _('Date Opened'),
                           'toggle':True},
            'ExpiryDate': {'title': _('Expiry Date'),
                           'index': 'getExpiryDate',
                           'toggle':True},
            'state_title': {'title': _('State'), 'toggle':True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Current'),
             'contentFilter':{'review_state':'current'},
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id':'expired',
             'title': _('Expired'),
             'contentFilter':{'review_state':'expired'},
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id':'disposed',
             'title': _('Disposed'),
             'contentFilter':{'review_state':'disposed'},
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate',
                         'state_title']},
        ]


    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        workflow = getToolByName(self.context, 'portal_workflow')
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if workflow.getInfoFor(obj, 'review_state') == 'current':
                # Check expiry date
                from Products.ATContentTypes.utils import DT2dt
                from datetime import datetime
                expirydate = DT2dt(obj.getExpiryDate()).replace(tzinfo=None)
                if (datetime.today() > expirydate):
                    workflow.doActionFor(obj, 'expire')
                    items[x]['review_state'] = 'expired'
                    items[x]['obj'] = obj
                    if 'review_state' in self.contentFilter \
                        and self.contentFilter['review_state'] == 'current':
                        continue
            items[x]['ID'] = obj.id
            items[x]['Manufacturer'] = obj.getReferenceManufacturer() and \
                 obj.getReferenceManufacturer().Title() or ''
            items[x]['Definition'] = obj.getReferenceDefinition() and \
                 obj.getReferenceDefinition().Title() or ''
            items[x]['DateSampled'] = self.ulocalized_time(obj.getDateSampled())
            items[x]['DateReceived'] = self.ulocalized_time(obj.getDateReceived())
            items[x]['DateOpened'] = self.ulocalized_time(obj.getDateOpened())
            items[x]['ExpiryDate'] = self.ulocalized_time(obj.getExpiryDate())

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/blank.png' \
                title='%s'>" % (self.portal_url, t(_('Blank')))
            if obj.getHazardous():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/hazardous.png' \
                title='%s'>" % (self.portal_url, t(_('Hazardous')))
            items[x]['replace']['ID'] = "<a href='%s/base_view'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['ID'], after_icons)
            outitems.append(items[x])
        return outitems


class ContactsView(BikaListingView):

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'SupplierContact',
            'path': {"query": "/".join(context.getPhysicalPath()),
                     "level": 0}
        }
        self.context_actions = {_('Add'):
            {'url': 'createObject?type_name=SupplierContact',
             'icon': '++resource++bika.lims.images/add.png'}
        }
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.icon = self.portal_url + "/++resource++bika.lims.images/contact_big.png"
        self.title = self.context.translate(_("Contacts"))

        self.columns = {
            'getFullname': {'title': _('Full Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
            'getFax': {'title': _('Fax')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['obj'].getFullname())

        return items
