from zope.interface import implements
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.interfaces import IProductItem
from bika.lims import config
from bika.lims.content.bikaschema import BikaSchema
from DateTime.DateTime import DateTime
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
import sys

schema = BikaSchema.copy() + Schema((
    StringField(
        'ProductItemID',
        searchable=True,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible=False,
            label=_("Product Item ID"),
        )
    ),
    ReferenceField('Product',
        required=1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types=('Product',),
        relationship='ProductItemProduct',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label = _("Product"),
            catalog_name='bika_setup_catalog',
            showOn=True,
        ),
    ),
    ComputedField('SupplierTitle',
        expression = 'context.getProduct().getSupplierTitle()',
        widget = ComputedWidget(
            label=_("Supplier"),
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('ProductCategoryTitle',
        expression = 'context.getProduct().getCategoryTitle()',
        widget = ComputedWidget(
            label=_("Product Category"),
            visible = {'edit':'hidden', }
        ),
    ),
    StringField('orderId',
        widget = StringWidget(
            label=_("Order Id"),
        )
    ),
    StringField('labId',
        widget = StringWidget(
            label=_("Lab Id"),
        )
    ),
    StringField('batchId',
        widget = StringWidget(
            label=_("Batch Id"),
        )
    ),
    StringField('location',
        widget = StringWidget(
            label=_("Location"),
        )
    ),
    DateTimeField('dateReceived',
        searchable = 1,
        widget = bika_DateTimeWidget(
            label = 'Date Received'
        ),
    ),
    DateTimeField('dateOpened',
        searchable = 1,
        widget = bika_DateTimeWidget(
            label = 'Date Opened'
        ),
    ),
    DateTimeField('expiryDate',
        searchable = 1,
        widget = bika_DateTimeWidget(
            label = 'Expiry Date'
        ),
    ),
    DateTimeField('disposalDate',
        searchable = 1,
        widget = bika_DateTimeWidget(
            label = 'Disposal Date'
        ),
    ),
    BooleanField(
        'IsStored',
        default=False,
        widget=BooleanWidget(visible=False),
    ),
    StringField('StorageLevelID',
        widget = StringWidget(
            label=_("Location"),
        )
    ),
))

schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema.moveField('ProductItemID', before='description')

class ProductItem(BaseContent):
    implements(IProductItem)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getProductTitle(self):
        return self.getProduct().Title()

    def getProductItemId(self):
        return self.getId()

registerType(ProductItem, config.PROJECTNAME)
