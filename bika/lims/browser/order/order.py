from Products.CMFPlone.utils import _createObjectByType
from zope import event

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter, methodcaller
from bika.lims.utils import to_utf8
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import t

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
            qty = float(item['Quantity'])
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
                if prodid.startswith('product_') and float(qty) > 0:
                    prodid = prodid.replace('product_', '')
                    product = [pro for pro in products if pro.getId() == prodid][0]
                    context.order_lineitems.append(
                            {'Product': prodid,
                             'Quantity': qty,
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
            qty = float(item['Quantity'])
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

