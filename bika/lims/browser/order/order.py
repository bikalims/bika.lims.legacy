from Products.CMFPlone.utils import _createObjectByType
from zope import event

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter, methodcaller
from bika.lims.utils import to_utf8
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import t
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
import itertools

class OrderView(BrowserView):
    template = ViewPageTemplateFile('templates/order_view.pt')
    title = _('Inventory Order')

    def __call__(self):
        context = self.context
        portal = self.portal
        setup = portal.bika_setup
        # Disabling the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())
        # Collect general data
        self.orderDate = self.ulocalized_time(context.getOrderDate())
        # self.supplier = context.getsupplier()
        # self.supplier = self.supplier.getFullname() if self.supplier else ''
        self.subtotal = '%.2f' % context.getSubtotal()
        self.vat = '%.2f' % context.getVATAmount()
        self.total = '%.2f' % context.getTotal()
        # Set the title
        self.title = context.Title()
        # Collect order item data
        items = context.order_lineitems
        products = context.aq_parent.objectValues('Product')
        self.items = []
        for item in items:
            prodid = item['Product']
            product = [pro for pro in products if pro.getId() == prodid][0]
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = item['Quantity']
            stored = item['Stored']
            all_stored = qty == stored
            self.items.append({
		        'title': product.Title(),
		        'description': product.Description(),
		        'unit': product.getUnit(),
		        'price': price,
		        'vat': '%s%%' % vat,
		        'quantity': qty,
		        'totalprice': '%.2f' % (price * qty),
                'prodid': prodid,
                'stored': stored,
                'all_stored': all_stored,
		    })
        self.items = sorted(self.items, key = itemgetter('title'))
        # Render the template
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()

class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/order_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        # Allow adding items to this context
        context.setConstrainTypesMode(0)
        # Collect the products
        products = context.aq_parent.objectValues('Product')
        # Handle for submission and regular request
    	if 'submit' in request:
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()
            # Clear the old line items
            context.order_lineitems = []
            # Process the order item data
            for prodid, qty in request.form.items():
                if prodid.startswith('product_') and int(qty) > 0:
                    prodid = prodid.replace('product_', '')
                    product = [pro for pro in products if pro.getId() == prodid][0]
                    context.order_lineitems.append(
                            {'Product': prodid,
                             'Quantity': int(qty),
                             'Stored': 0,
                             'Price': product.getPrice(),
                             'VAT': product.getVAT()})

            # Redirect to the list of orders
            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return
        else:
            self.orderDate = context.Schema()['OrderDate']
            self.subtotal = '%.2f' % context.getSubtotal()
            self.vat = '%.2f' % context.getVATAmount()
            self.total = '%.2f' % context.getTotal()
            # Prepare the products
            items = context.order_lineitems
            self.products = []
            products = sorted(products, key = methodcaller('Title'))
            for product in products:
                item = [o for o in items if o['Product'] == product.getId()]
                quantity = item[0]['Quantity'] if len(item) > 0 else 0
                self.products.append({
                    'id': product.getId(),
                    'title': product.Title(),
                    'description': product.Description(),
                    'unit': product.getUnit(),
                    'price': product.getPrice(),
                    'vat': '%s%%' % product.getVAT(),
                    'quantity': quantity,
                    'total': (float(product.getPrice()) * float(quantity)),
                })
            # Render the template
            return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()

class PrintView(OrderView):

    template = ViewPageTemplateFile('templates/order_print.pt')
    view_template = ViewPageTemplateFile('templates/order_view.pt')

    def __call__(self):
        context = self.context
        self.orderDate = context.getOrderDate()
        products = context.aq_parent.objectValues('Product')
        items = context.order_lineitems
        self.items = []
        for item in items:
            prodid = item['Product']
            product = [pro for pro in products if pro.getId() == prodid][0]
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = item['Quantity']
            self.items.append({
                'title': product.Title(),
                'description': product.Description(),
                'unit': product.getUnit(),
                'price': price,
                'vat': '%s%%' % vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty)
            })
        self.items = sorted(self.items, key = itemgetter('title'))
        self.subtotal = '%.2f' % context.getSubtotal()
        self.vat = '%.2f' % context.getVATAmount()
        self.total = '%.2f' % context.getTotal()
        self.supplier = self._supplier_data()
        return self.template()

    def _supplier_data(self):
        data = {}
        supplier = self.context.aq_parent
        if supplier:
            data['obj'] = supplier
            data['id'] = supplier.id
            data['title'] = supplier.Title()
            data['url'] = supplier.absolute_url()
            data['name'] = to_utf8(supplier.getName())
            data['phone'] = to_utf8(supplier.getPhone())
            data['fax'] = to_utf8(supplier.getFax())

            supplier_address = supplier.getPostalAddress()
            if supplier_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = ["<div>%s</div>" % supplier_address.get(v) for v in _keys
                         if supplier_address.get(v)]
                supplier_address = "".join(_list)
            else:
                supplier_address = ''
            data['address'] = to_utf8(supplier_address)
            data['email'] = to_utf8(supplier.getEmailAddress())
        return data

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class OrderStore(BrowserView):

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        # Allow adding items to this context
        context.setConstrainTypesMode(0)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        catalog = [pi.getObject() for pi in bsc(portal_type='ProductItem')]
        # Remaining product items of this order
        productitems = [pi for pi in catalog \
                            if (pi.getOrderId() == self.context.getId() and
                                pi.getIsStored() == False)]
        # Organize items as per their product
        products_dict = {}
        for pi in productitems:
            product_id = pi.getProduct().getId()
            if not product_id in products_dict:
                products_dict[product_id] = []
            products_dict[product_id].append(pi)
        # Product names against their IDs used for error messages
        product_names = {}
        products = context.aq_parent.objectValues('Product')
        for pr in products:
            product_names[pr.getId()] = pr.Title()

        if not 'submit' in request:
            request.response.redirect(context.absolute_url_path())
            return
        # Process form inputs
        portal_factory = getToolByName(context, 'portal_factory')
        context = portal_factory.doCreate(context, context.id)
        context.processForm()
        levels = [sl.getObject() for sl in bsc(portal_type='StorageLevel')]

        for name in request.form:
            if not name.startswith('storage-'):
                continue
            product_id = name.lstrip('storage-')
            product_name = product_names[product_id]
            # Get available storage levels under parent
            hierarchy = request.form[name]
            child_levels = [sl for sl in levels \
                                if (hasattr(sl.aq_parent, 'getHierarchy') and
                                    sl.aq_parent.getHierarchy() == hierarchy and
                                    not sl.getHasChildren() and
                                    not sl.getIsOccupied())]
            productitems = products_dict[product_id]
            # Get number of items to store
            nid = 'number-' + product_id
            if nid in request.form and request.form[nid]:
                number = int(request.form[nid])
            else:
                continue
            # Validate number and storage levels
            if number < 1:
                continue
            message = ''
            if number > len(productitems):
                message = _('Number entered for ' + product_name + ' is invalid.')
            if not child_levels:
                message = 'Storage level is required. Please correct.'
            if number > len(child_levels):
                message = 'The number entered for %s is %d but the ' \
                          'storage level ( %s ) only has %d spaces.' % (
                             product_name, number, hierarchy, len(child_levels))
            if message:
                self.context.plone_utils.addPortalMessage(_(message), 'error')
                continue

            # Store product items in available levels
            productitems = productitems[:number]
            for i, pi in enumerate(productitems):
                level = child_levels[i]
                pi.setStorageLevelID(level.getId())
                pi.setIsStored(True)
                level.setProductItemID(pi.getId())
                level.setIsOccupied(True)
                # Decrement number of available children of parent
                nac = level.aq_parent.getNumberOfAvailableChildren()
                level.aq_parent.setNumberOfAvailableChildren(nac - 1)
                # Increment number of items stored in Order view
                for lineitem in self.context.order_lineitems:
                    if lineitem['Product'] == product_id:
                        lineitem['Stored'] = lineitem['Stored'] + 1
        request.response.redirect(context.absolute_url_path())
        return


class OrderPathBarViewlet(ViewletBase):
    """Viewlet for overriding breadcrumbs in Order View"""

    index = ViewPageTemplateFile('templates/path_bar.pt')

    def update(self):
        super(OrderPathBarViewlet, self).update()
        self.is_rtl = self.portal_state.is_rtl()
        breadcrumbs = getMultiAdapter((self.context, self.request),
                                      name='breadcrumbs_view').breadcrumbs()
        breadcrumbs[2]['absolute_url'] += '/orders'
        self.breadcrumbs = breadcrumbs
