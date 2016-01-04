from AccessControl.SecurityManagement import newSecurityManager
from Products.Archetypes import Field
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite

import openpyxl

import argparse
import os
import pprint
import shutil
import tempfile
import transaction
import zipfile


class Import:
    def __init__(self, args):
        self.args = args
        self.deferred = []

    def __call__(self):
        """Export entire bika site
        """
        # pose as user
        self.user = app.acl_users.getUserById(self.args.username)
        newSecurityManager(None, self.user)
        # get or create portal object
        try:
            self.portal = app.unrestrictedTraverse(self.args.sitepath)
        except KeyError:
            self.portal = self.create_site()
        setSite(self.portal)
        # Extract zipfile
        self.tempdir = tempfile.mkdtemp()
        zf = zipfile.ZipFile(self.args.inputfile, 'r')
        zf.extractall(self.tempdir)
        # Open workbook
        self.wb = openpyxl.load_workbook(
                os.path.join(self.tempdir, 'setupdata.xlsx'))
        # Import
        self.import_laboratory()
        self.import_bika_setup()
        self.import_portal_types()
        # Remove tempdir
        shutil.rmtree(self.tempdir)

        # Resolve deferred/circular references
        self.solve_deferred()

        # Rebuild catalogs
        for c in ['bika_analysis_catalog',
                  'bika_catalog',
                  'bika_setup_catalog',
                  'portal_catalog']:
            print 'rebuilding %s' % c
            self.portal[c].clearFindAndRebuild()

        transaction.commit()

    def create_site(self):
        profiles = default_profiles
        if self.args.profiles:
            profiles.extend(self.args.profiles)
        addPloneSite(
                app,
                self.args.sitepath,
                title=self.args.title,
                profile_id=_DEFAULT_PROFILE,
                extension_ids=profiles,
                setup_content=True,
                default_language=self.args.language
        )
        self.portal = app.unrestrictedTraverse(self.args.sitepath)
        return self.portal

    def get_catalog(self, portal_type):
        """grab the first catalog we are indexed in
        """
        at = getToolByName(self.portal, 'archetype_tool')
        return at.getCatalogsByType(portal_type)[0]

    def resolve_reference_ids_to_uids(self, instance, field, value):
        """Get target UIDs for any ReferenceField.
        If targets do not exist, the requirement is added to deferred.
        """
        # We make an assumption here, that if there are multiple allowed
        # types, they will all be indexed in the same catalog.
        target_type = field.allowed_types \
            if isinstance(field.allowed_types, basestring) \
            else field.allowed_types[0]
        catalog = self.get_catalog(target_type)
        # The ID is what is stored in the export, so first we must grab these:
        if field.multiValued:
            # multiValued references get their values stored in a sheet
            # named after the relationship.
            ids = []
            if field.relationship[:31] not in self.wb:
                return None
            ws = self.wb[field.relationship[:31]]
            ids = []
            for rownr, row in enumerate(ws.rows):
                if rownr == 0:
                    keys = [cell.value for cell in row]
                    continue
                rowdict = dict(zip(keys, [cell.value for cell in row]))
                if rowdict['Source'] == instance.id:
                    ids.append(rowdict['Target'])
            if not ids:
                return []
            final_value = []
            for vid in ids:
                brain = catalog(portal_type=field.allowed_types, id=vid)
                if brain:
                    final_value.append(brain[0].getObject())
                else:
                    self.defer(instance, field, catalog,
                               field.allowed_types, vid)
            return final_value
        else:
            if value:
                brain = catalog(portal_type=field.allowed_types, id=value)
                if brain:
                    return brain[0].getObject()
                else:
                    self.defer(instance, field, catalog,
                               field.allowed_types, value)
        return None

    def resolve_records(self, instance, field, value):
        # RecordField and RecordsField
        # We must re-create the dict (or list of dicts) from sheet values
        ws = self.wb[value]
        matches = []
        for rownr, row in enumerate(ws.rows):
            if rownr == 0:
                keys = [cell.value for cell in row]
                continue
            rowdict = dict(zip(keys, [cell.value for cell in row]))
            if rowdict['id'] == instance.id \
                    and rowdict['field'] == field.getName():
                matches.append(rowdict)
        if type(field.default) == dict:
            return matches[0] if matches else {}
        else:
            return matches

    def set(self, instance, field, value):
        # mutator = field.getMutator(instance)
        outval = self.mutate(instance, field, value)
        if field.getName() == 'id':
            # I don't know why, but if we use field.set for setting the id, it
            # lands in the database as a unicode string causing catalog failure
            instance.id = outval
        else:
            field.set(instance, outval)

    def mutate(self, instance, field, value):
        # Ints and bools are transparent
        if type(value) in (int, bool):
            return value
        # All strings must be encoded
        if isinstance(value, unicode):
            value = value.encode('utf-8')

        # RecordField is a single dictionary from the lookup table
        if isinstance(field, RecordField):
            value = self.resolve_records(instance, field, value) \
                if value else {}
        # RecordsField is a list of dictionaries from the lookup table
        elif isinstance(field, RecordsField) or \
                (isinstance(value, basestring)
                 and value
                 and value.endswith('_values')):
            value = self.resolve_records(instance, field, value) \
                if value else []

        # ReferenceField looks up single ID from cell value, or multiple
        # IDs from a lookup table
        if Field.IReferenceField.providedBy(field):
            value = self.resolve_reference_ids_to_uids(instance, field, value)
        # LinesField was converted to a multiline string on export
        if Field.ILinesField.providedBy(field):
            value = value.splitlines() if value else ()
        # XXX THis should not be reading entire file contents into mem.
        # TextField provides the IFileField interface, these must be ignored.
        elif value and Field.IFileField.providedBy(field) \
                and not Field.ITextField.providedBy(field):
            if not os.path.exists(os.path.join(self.tempdir, value)):
                print "Expected file does not exist: " + value
                return ''
            value = open(os.path.join(self.tempdir, value)).read()
        return value

    def import_laboratory(self):
        instance = self.portal.bika_setup.laboratory
        schema = instance.schema
        ws = self.wb['Laboratory']
        for row in ws.rows:
            fieldname = row[0].value
            cellvalue = row[1].value
            field = schema[fieldname]
            self.set(instance, field, cellvalue)

    def import_bika_setup(self):
        instance = self.portal.bika_setup
        schema = instance.schema
        ws = self.wb['BikaSetup']
        for row in ws.rows:
            fieldname = row[0].value
            cellvalue = row[1].value
            field = schema[fieldname]
            self.set(instance, field, cellvalue)

    def import_portal_types(self):
        pt = getToolByName(self.portal, 'portal_types')
        for sheetname in self.wb.get_sheet_names():
            if sheetname in ['Laboratory', 'BikaSetup']:
                continue
            if sheetname in pt:
                self.import_portal_type(sheetname)

    def import_portal_type(self, portal_type):
        pt = getToolByName(self.portal, 'portal_types')
        fti = pt[portal_type]
        ws = self.wb[portal_type]
        keys = [cell.value for cell in ws.rows[0]]
        for rownr, row in enumerate(ws.rows[1:]):
            rowdict = dict(zip(keys, [cell.value for cell in row]))
            # First, some fields we manually extract, to prevent them
            # from being handled by the loop below:
            path = rowdict['path'].encode('utf-8').strip('/').split('/')
            del (rowdict['path'])
            uid = rowdict['uid'].encode('utf-8')
            del (rowdict['uid'])
            instance_id = rowdict['id'].encode('utf-8')
            del (rowdict['id'])
            # We need to get 'title', for the case of aberrations with no value
            # it's really required, so we use the ID in these cases.
            title = rowdict['title'].encode('utf-8') if rowdict['title'] \
                else instance_id
            del (rowdict['title'])

            parent = self.portal.unrestrictedTraverse(path)
            instance = fti.constructInstance(parent, instance_id, title=title)
            instance.unmarkCreationFlag()
            instance.reindexObject()
            for fieldname, value in rowdict.items():
                field = instance.schema[fieldname]
                self.set(instance, field, value)

    def defer(self, instance, field, catalog, allowed_types, target_id):
        self.deferred.append({
            'instance': instance,
            'field': field,
            'catalog': catalog,
            'allowed_types': allowed_types,
            'target_id': target_id,
        })

    def solve_deferred(self):
        # walk through self.deferred and link outstanding references
        if self.deferred:
            print 'Attempting to solve %s deferred reference targets' % \
                  len(self.deferred)
        nr_unsolved = [0, len(self.deferred)]
        while nr_unsolved[-1] > nr_unsolved[-2]:
            unsolved = []
            for d in self.deferred:
                src_obj = d['instance']
                src_field = d['field']
                target_id = d['target_id']
                allowed_types = d['allowed_types']
                catalog = d['catalog']

                try:
                    proxies = catalog(portal_type=allowed_types, id=target_id)
                except:
                    continue
                if len(proxies) > 0:
                    obj = proxies[0].getObject()
                    if src_field.multiValued:
                        value = src_field.get(src_obj)
                        if obj.UID() not in value:
                            value.append(obj.UID())
                    else:
                        value = obj.UID()
                    src_field.set(src_obj, value)
                else:
                    unsolved.append(d)
            self.deferred = unsolved
            nr_unsolved.append(len(unsolved))
        if self.deferred:
            print 'Failed to solve %s deferred targets:' % len(self.deferred)
            pprint.pprint(self.deferred)
