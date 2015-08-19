from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IStorageLevel
from bika.lims.interfaces import IStorageLevelIsAssignable
from bika.lims.utils import t
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from zope.interface import alsoProvides, noLongerProvides
from zope.interface import implements

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
    ComputedField(
        'ParentUID',
        expression='context.aq_parent.UID()',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    BooleanField(
        'HasChildren',
        default=False,
        widget=BooleanWidget(visible=False),
    ),
    IntegerField(
        'NumberOfAvailableChildren',
        default=0,
        widget=IntegerWidget(visible=False)
    ),
    ComputedField(
        'StorageLevelID',
        expression='context.getId()',
        widget=ComputedWidget(visible=False),
    ),
    BooleanField(
        'IsOccupied',
        default=0,
        widget=BooleanWidget(visible=False),
    ),
    StringField(
        'ProductItemID',
        widget=StringWidget(visible=False),
    ),
    ComputedField(
        'Hierarchy',
        expression='context.getHierarchy()',
        widget=ComputedWidget(visible=False,),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class StorageLevel(ATFolder):
    implements(IStorageLevel)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        renameAfterCreation(self)

    def at_post_create_script(self):
        # Jira LIMS-1961
        if hasattr(self.aq_parent, 'getNumberOfAvailableChildren'):
            number = self.aq_parent.getNumberOfAvailableChildren()
            self.aq_parent.setNumberOfAvailableChildren(number + 1)
            alsoProvides(self.aq_parent, IStorageLevelIsAssignable)
            self.aq_parent.reindexObject(idxs=['object_provides'])

        if hasattr(self.aq_parent, 'HasChildren') and not \
                self.aq_parent.HasChildren:
            self.aq_parent.setHasChildren(True)
            grand_parent = self.aq_parent.aq_parent

            if hasattr(self.aq_parent, 'aq_parent') and \
                    hasattr(grand_parent, 'getNumberOfAvailableChildren'):
                number = grand_parent.getNumberOfAvailableChildren()
                grand_parent.setNumberOfAvailableChildren(number - 1)

                if number <= 1:
                    noLongerProvides(grand_parent, IStorageLevelIsAssignable)
                    grand_parent.reindexObject(idxs=['object_provides'])

    def getHierarchy(self):
        ancestors = []
        ancestor = self
        while(1):
            ancestors.append(ancestor.Title())
            if ancestor.portal_type == 'StorageUnit':
                break
            ancestor = ancestor.aq_parent
        return ' > '.join(reversed(ancestors))

registerType(StorageLevel, PROJECTNAME)
