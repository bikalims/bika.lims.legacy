"""
Catalog Dexterity Objects that appear in more than one catalog
"""
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import ManageSupplyOrders, ManageLoginDetails


def indexObject(obj, event):
    """ Various types need automation on edit.
    """
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type not in ('ClientType', 'ClientDepartment'):
        return

    if not hasattr(obj, '_catalogs'):
        return

    for c in obj._catalogs():
        c.catalog_object(obj)

def unIndexObject(obj, event):
    ''' remove an object from all registered catalogs '''
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type not in ('ClientType', 'ClientDepartment'):
        return

    if not hasattr(obj, '_catalogs'):
        return

    path = '/'.join(obj.getPhysicalPath())
    for c in obj._catalogs():
        c.uncatalog_object(path)

def reIndexObject(obj, event, idxs=[]):
    ''' reindex object '''
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type not in ('ClientType', 'ClientDepartment'):
        return

    if not hasattr(obj, '_catalogs'):
        return

    if idxs == []:
        # Update the modification date.
        if hasattr(aq_base(obj), 'notifyModified'):
            obj.notifyModified()
    for c in obj._catalogs():
        if c is not None:
            c.reindexObject(obj)


def reIndexObjectSecurity(obj, event, skip_self=False):
    ''' reindex only security information on catalogs '''
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type not in ('ClientType', 'ClientDepartment'):
        return

    if not hasattr(obj, '_catalogs'):
        return

    path = '/'.join(obj.getPhysicalPath())
    for c in obj._catalogs():
        for brain in c.unrestrictedSearchResults(path=path):
            brain_path = brain.getPath()
            if brain_path == path and skip_self:
                continue
            # Get the object
            ob = brain._unrestrictedGetObject()

            # Recatalog with the same catalog uid.
            # _cmf_security_indexes in CMFCatalogAware
            c.reindexObject(ob,
                            idxs=obj._cmf_security_indexes,
                            update_metadata=0,
                            uid=brain_path)

