from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import tmpID
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.lims.interfaces import IStorageLevels

class StorageLevelsView(BikaListingView):
    template = ViewPageTemplateFile('templates/storagelevels.pt')
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageLevelsView, self).__init__(context, request)
        path = '/'.join(self.context.getPhysicalPath())
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageLevel',
                              'sort_on': 'sortable_title',
                              'path': {'query': path, 'depth': 1}}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=StorageLevel',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = (hasattr(self.context, 'Title') and self.context.Title() or
                      self.context.translate(_("Storage Levels")))
        self.icon = self.portal_url
        self.icon += "/++resource++bika.lims.images/storagelocation_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                                'toggle': True},
            'Hierarchy': {'title': _('Hierarchy'),
                                'toggle': False},
            'ProductItemID': {'title': _('Product Item ID'),
                                'toggle': True},
            'IsOccupied': {'title': _('Is Occupied'),
                                'toggle': False},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'Hierarchy',
                         'ProductItemID',
                         'IsOccupied']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'Hierarchy',
                         'ProductItemID',
                         'IsOccupied']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         'Hierarchy',
                         'ProductItemID',
                         'IsOccupied']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['ProductItemID'] = obj.getProductItemID()
            items[x]['IsOccupied'] = 'yes' if obj.getIsOccupied() else 'no'
            items[x]['Hierarchy'] = obj.getHierarchy()
        return items


class AddStorageLevelView(BrowserView):
    """ Handler for the "Add Storage levels" button in Storage levels
        view.
    """

    def StorageLevelTitleExists(self, title):
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        #XXX ParentUID should be queried instead of looping
        for item in catalog(portal_type='StorageLevel', title=title):
            if item.getObject().getParentUID() == self.context.UID():
                return True
        return False

    def RepresentsInt(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __call__(self):
        form = self.request.form
        title = self.request.get('storagelevel-title', '')
        sequencestart = self.request.get('storagelevel-sequencestart', '')
        number = self.request.get('storagelevel-number', '')

        if not title and not number:
            message = ('error', ('Either the storage level title or the number '
                                'of items should be specified.'))
        elif number and (not self.RepresentsInt(number) or int(number) < 1):
            message = ('error', 'Number of items should be a positive integer.')
        elif sequencestart and (not self.RepresentsInt(sequencestart) or
                int(sequencestart) < 0):
            message = ('error', 'Sequence start should be non-negative integer.')
        else:
            separator = title and number and \
                self.context.bika_setup.getStorageLevelTitleSeparator() or ''
            sequencestart = sequencestart and int(sequencestart) or 1
            number = number and int(number) or 1

            for index in range(number):
                sequenced_index = number is not 1 and str(sequencestart+index) or ''
                indexed_title = title + separator + sequenced_index

                if self.StorageLevelTitleExists(indexed_title):
                    title_exists_message = True
                    message = _('Some titles already exist. '
                                'Those were not created to maintain the '
                                'uniqueness of titles.')
                    self.context.plone_utils.addPortalMessage(message, 'warning')
                    continue
                sl = _createObjectByType('StorageLevel', self.context, tmpID())
                sl.setTitle(indexed_title)
                sl.processForm()
            message = ('info', 'Changes saved.')
        self.context.plone_utils.addPortalMessage(_(message[1]), message[0])
        self.request.RESPONSE.redirect(self.context.absolute_url())
        return


schema = ATFolderSchema.copy()
class StorageLevels(ATFolder):
    implements(IStorageLevels)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StorageLevels, PROJECTNAME)
