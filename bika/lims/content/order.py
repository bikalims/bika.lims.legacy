from Products.Archetypes.public import *
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as BikaReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IOrder
from bika.lims.utils import t
from DateTime import DateTime
from persistent.mapping import PersistentMapping
from decimal import Decimal
from Products.Archetypes import atapi
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFPlone.utils import safe_unicode
from zope.component import getAdapter
from zope.interface import implements
from bika.lims.workflow import doActionFor


schema = BikaSchema.copy() + Schema((
    StringField('OrderNumber',
                required=1,
                searchable=True,
                widget=StringWidget(
                    label=_("Order Number"),
                    ),
                ),
    DateTimeField(
      'OrderDate',
      required=1,
      default_method='current_date',
      widget=DateTimeWidget(
        label=_("Order Date"),
        size=12,
        render_own_label=True,
        visible={
          'edit': 'visible',
          'view': 'visible',
          'add': 'visible',
          'secondary': 'invisible'
        },
      ),
    ),
    DateTimeField('DateDispatched',
                  widget=DateTimeWidget(
                      label=_("Date Dispatched"),
                      ),
                  ),
    DateTimeField('DateReceived',
                  widget=DateTimeWidget(
                      label=_("Date Received"),
                      ),
                  ),
    DateTimeField('DateStored',
                  widget=DateTimeWidget(
                      label=_("Date Stored"),
                      ),
                  ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),
    ComputedField('SupplierUID',
                  expression = 'here.aq_parent.UID()',
                  widget = ComputedWidget(
                      visible=False,
                      ),
                  ),
    ComputedField('ProductUID',
                  expression = 'context.getProductUIDs()',
                  widget = ComputedWidget(
                      visible=False,
                      ),
                  ),
),
)

schema['title'].required = False

class OrderLineItem(PersistentMapping):
    pass

class Order(BaseFolder):

    implements(IOrder, IConstrainTypes)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    order_lineitems = []

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the OrderNumber as title """
        return safe_unicode(self.getOrderNumber()).encode('utf-8')

    def getOrderNumber(self):
        return safe_unicode(self.getId()).encode('utf-8')

    def getSuppliers(self):
        adapter = getAdapter(self.aq_parent, name='getSuppliers')
        return adapter()

    security.declareProtected(View, 'getTotalQty')
    def getTotalQty(self):
        """ Compute total qty """
        if self.order_lineitems:
            return sum(
                [obj['Quantity'] for obj in self.order_lineitems])
        return 0

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal """
        if self.order_lineitems:
            return sum(
                [(Decimal(obj['Quantity']) * Decimal(obj['Price'])) for obj in self.order_lineitems])
        return 0

    security.declareProtected(View, 'getVATAmount')
    def getVATAmount(self):
        """ Compute VAT """
        return Decimal(self.getTotal()) - Decimal(self.getSubtotal())

    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """ Compute TotalPrice """
        total = 0
        for lineitem in self.order_lineitems:
            total += Decimal(lineitem['Quantity']) * \
                     Decimal(lineitem['Price']) *  \
                     ((Decimal(lineitem['VAT']) /100) + 1)
        return total

    def workflow_script_dispatch(self):
        """ dispatch order """
        self.setDateDispatched(DateTime())
        self.reindexObject()
        # Order publish preview
        import zExceptions, transaction
        transaction.commit()
        raise zExceptions.Redirect(self.absolute_url() + "/publish")

    def workflow_script_receive(self):
        """ receive order """
        self.setDateReceived(DateTime())
        self.reindexObject()

    def workflow_script_store(self):
        """ store order """
        self.setDateStored(DateTime())
        self.reindexObject()

    security.declareProtected(View, 'getProductUIDs')
    def getProductUIDs(self):
        """ return the uids of the products referenced by order items
        """
        uids = []
        for orderitem in self.objectValues('OrderItem'):
            product = orderitem.getProduct()
            if product is not None:
                uids.append(orderitem.getProduct().UID())
        return uids

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()


atapi.registerType(Order, PROJECTNAME)