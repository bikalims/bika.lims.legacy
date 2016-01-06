import csv

from Products.Archetypes import Field
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.CMFCore.utils import getToolByName
from zExceptions import Redirect

from bika.lims import bikaMessageFactory as _

import os
import pprint
import shutil
import tempfile
import zipfile

from bika.lims.browser import BrowserView

class Import(BrowserView):
    def __init__(self, context, request):
        super(Import, self).__init__(context, request)

        # We'll extract the ZIP file here; any other tmp stuff can be done
        # here too, since we rmtree it later.
        self.tempdir = tempfile.mkdtemp()

        # If a reference field refers to an item which is not yet imported,
        # an entry is stored in self.deferred.  After importing is complete,
        # we step through this list and try to resolve outstanding references.
        self.deferred = []

        # I store the UID of all objects when the export was done.
        # The newly created objects will have fresh UIDs.
        # I keep a map of old<->new UIDs here for quick lookup.
        self.old2newuid = {}
        self.new2olduid = {}

        # Quick lookup of values for Record and Records fields.
        self.records = {}

        # Quick lookup of values for Reference fields.
        self.references = {}

        # If some portal_type can't be imported becaues the heirarchy is not
        # yet in place, it's added to self.outstanding, and attempted again after
        # successfully imported types have been created.  The key is portal_type.
        self.outstanding = {}

    def __call__(self):
        """
        """
        self.validate_request()
        self.extract_zip()
        # Manually import laboratory and bika_setup
        self.import_laboratory()
        self.import_bika_setup()
        self.import_portal_types()

        # Remove tempdir
        shutil.rmtree(self.tempdir)

        # Resolve deferred/circular references
        self.solve_deferred()

        # Rebuild catalogs
        # XXX do this incrementally; large imports it will take ages.
        for c in ['bika_analysis_catalog',
                  'bika_catalog',
                  'bika_setup_catalog',
                  'portal_catalog']:
            print 'rebuilding %s' % c
            self.portal[c].clearFindAndRebuild()

    def validate_request(self):
        if 'file' not in self.request.form \
                or not hasattr(self.request.form['file'], 'filename'):
            message = _('No file selected')
            self.context.plone_utils.addPortalMessage(message, 'warn')
            url = self.context.absolute_url() + '/bika_setupdata'
            shutil.rmtree(self.tempdir)
            raise Redirect, url

    def extract_zip(self):
        """Throw all files in the selected zip file into a
        temporary folder
        """
        try:
            zf = zipfile.ZipFile(self.request.form['file'], 'r')
            zf.extractall(self.tempdir)
        except zipfile.BadZipfile:
            message = _('Bad zip file submitted')
            self.context.plone_utils.addPortalMessage(message, 'warn')
            url = self.context.absolute_url() + '/bika_setupdata'
            shutil.rmtree(self.tempdir)
            raise Redirect, url

    def import_laboratory(self):
        """Manually import the Laboratory fields, this CSV
        file uses a different layout.
        """
        instance = self.portal.bika_setup.laboratory
        schema = instance.schema
        fn = os.path.join(self.tempdir, 'Laboratory.csv')
        with open(fn, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fieldname = row['field']
                fieldvalue = row['value']
                field = schema[fieldname]
                self.set(instance, field, fieldvalue)

    def import_bika_setup(self):
        """Manually import the BikaSetup fields, this CSV
        file uses a different layout.
        """
        instance = self.portal.bika_setup
        schema = instance.schema
        fn = os.path.join(self.tempdir, 'BikaSetup.csv')
        with open(fn, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fieldname = row['field']
                fieldvalue = row['value']
                field = schema[fieldname]
                self.set(instance, field, fieldvalue)

    def import_portal_types(self):
        """Import all portal_types
        """
        for portal_type in self.list_portal_types():
            self.import_portal_type(portal_type)
        while self.outstanding:
            outstanding, self.outstanding = self.outstanding, {}
            for portal_type, items in outstanding.items():
                for rowvalues in items:
                    self.create_instance(portal_type, rowvalues)

    def list_portal_types(self):
        """List portal type names which have a corrosponding CSV file
        """
        portal_types = []
        pt = getToolByName(self.portal, 'portal_types')
        for fn in os.listdir(self.tempdir):
            basename = os.path.splitext(fn)[0]
            if basename in ['Laboratory', 'BikaSetup']:
                continue
            if basename in pt:
                portal_types.append(basename)
        return portal_types

    def import_portal_type(self, portal_type):
        """Convert rows in a CSV into objects in the database.
        """
        fn = os.path.join(self.tempdir, portal_type + ".csv")
        with open(fn, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.create_instance(portal_type, row)

    def create_instance(self, portal_type, rowvalues):
        """Create an object from a CSV row
        """
        # I don't care about these fields in the schema; they are handled
        # manually.  But, I must keep them in rowvalues, so that any
        # retried creation attempts still have this information
        schema_ignore = ['path', 'uid', 'id', 'title']

        path = rowvalues['path'].encode('utf-8').strip('/').split('/')
        old_uid = rowvalues['uid'].encode('utf-8')
        instance_id = rowvalues['id'].encode('utf-8')
        # We need to get 'title', for the case of aberrations with no value
        # it's really required, so we use the ID in these cases.
        title = rowvalues['title'] if rowvalues['title'] \
            else instance_id

        pt = getToolByName(self.portal, 'portal_types')
        fti = pt[portal_type]

        try:
            parent = self.portal.unrestrictedTraverse(path)
        except AttributeError:
            # So some parent element does not exist.  It will be attempted
            # again later.
            if portal_type not in self.outstanding:
                self.outstanding[portal_type] = []
            self.outstanding[portal_type].append(rowvalues)
            return

        instance = fti.constructInstance(parent, instance_id, title=title)
        instance.unmarkCreationFlag()
        instance.reindexObject()
        self.old2newuid[old_uid] = instance.UID()
        self.new2olduid[instance.UID()] = old_uid
        for fieldname, value in rowvalues.items():
            if fieldname in schema_ignore:
                continue
            field = instance.schema[fieldname]
            self.set(instance, field, value)

    def set(self, instance, field, value):
        # mutator = field.getMutator(instance)
        outval = self.mutate(instance, field, value)
        if field.getName() == 'id':
            # if we use field.set for setting the id, it lands in the
            # database as a unicode string causing catalog failure
            instance.id = outval
        else:
            field.set(instance, outval)

    def mutate(self, instance, field, value):
        # bools are transparent
        if type(value) is bool:
            return value
        # Int must be reconstituted
        if type(value) is int:
            if value:
                value = int(value)
            return value
        # All unicode strings must be encoded
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        # RecordField is a single dictionary from the lookup table
        if isinstance(field, RecordField):
            value = self.resolve_records(instance, field, value)
        # RecordsField is a list of dictionaries from the lookup table
        elif isinstance(field, RecordsField):
            value = self.resolve_records(instance, field, value)
        # ReferenceField looks up single ID from cell value, or multiple
        # IDs from a lookup table
        if Field.IReferenceField.providedBy(field):
            if not field.multiValued and not value:
                return value
            value = self.resolve_references(instance, field, value)
        # LinesField was converted to a multiline string on export
        if Field.ILinesField.providedBy(field):
            value = value.split('\\n') if value else ()
        # TextField provides the IFileField interface, these must be ignored.
        elif value and Field.IFileField.providedBy(field) \
                and not Field.ITextField.providedBy(field):
            if not os.path.exists(os.path.join(self.tempdir, value)):
                print "Expected file does not exist: " + value
                return ''
            value = open(os.path.join(self.tempdir, value)).read()
        return value

    def resolve_references(self, instance, field, value):
        """Return the target object(s) of the reference field.
        If any of the targets do not exist, the requirement is
        added to self.deferred.
        """
        catalog = self.get_catalog(field)
        if field.multiValued:
            # reference_lookup_init only valid for multiValued
            self.reference_lookup_init(field.relationship)
            target_uids = []
            for rowvalues in self.references[field.relationship]:
                if rowvalues['source_uid'] == self.new2olduid[instance.UID()]:
                    # if the object has been created, it will be mappedin old2newuid
                    old_target_uid = rowvalues['target_uid']
                    if old_target_uid in self.old2newuid:
                        target_uids.append(self.old2newuid[old_target_uid])
                    else:
                        # defer accepts the OLD uid
                        self.defer(instance, field, field.allowed_types,
                                   old_target_uid)
            return target_uids
        else:
            # if the object has been created, it will be mapped in old2newuid
            if value in self.old2newuid:
                return self.old2newuid[value]
            else:
                # defer accepts the OLD uid
                self.defer(instance, field, field.allowed_types, value)
        return None

    def reference_lookup_init(self, relationship):
        """When I resolve Reference fields, the values are stored in
        a separate CSV file. Instead of opening it and closing it
        each time a field value is required, I just store the entire
        lot in self.references for quick lookup. The relationship
        name is the key.
        """
        if relationship not in self.references:
            self.references[relationship] = []
            fn = os.path.join(self.tempdir, relationship + ".csv")
            if os.path.exists(fn):
                with open(fn, 'rb') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.references[relationship].append(row)

    def get_catalog(self, field):
        """grab the first catalog we are indexed in
        We make an assumption here, that if there are multiple allowed
        types, they will all be indexed in the same catalog.
        """
        target_type = field.allowed_types \
            if isinstance(field.allowed_types, basestring) \
            else field.allowed_types[0]
        at = getToolByName(self.portal, 'archetype_tool')
        return at.getCatalogsByType(target_type)[0]

    def resolve_records(self, instance, field, value):
        """Retrieve dictionary values for Records and Record fields
        (Dictionary and List of Dictionary)
        """
        self.records_lookup_init(instance, field)
        key = instance.portal_type + '_' + field.getName()
        fieldvalue = []
        for record in self.records[key]:
            if record['instance_id'] == instance.id:
                fieldvalue.append(record)
        # Only going to return a single value for single valued fields
        if type(field.default) == dict:
            return fieldvalue[0] if fieldvalue else {}
        else:
            return fieldvalue

    def records_lookup_init(self, instance, field):
        """When I resolve Records and Record fields (dict or list of dict)
        the values are stored in a separate CSV file. Instead of opening
        it and closing it each time a field value is required, I just
        store the entire lot in self.records for quick lookup. The key
        is the same as the filename of the CSV, sans extension.
        """
        key = instance.portal_type + '_' + field.getName()
        if key not in self.records:
            self.records[key] = []
            fn = os.path.join(self.tempdir, key + ".csv")
            if os.path.exists(fn):
                with open(fn, 'rb') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.records[key].append(row)

    def defer(self, instance, field, allowed_types, target_uid):
        if not target_uid:
            import pdb;pdb.set_trace()
        self.deferred.append({
            'instance': instance,
            'field': field,
            'allowed_types': allowed_types,
            'target_uid': target_uid,
        })

    def solve_deferred(self):
        # walk through self.deferred and link outstanding references
        if self.deferred:
            print 'Attempting to solve %s deferred reference targets' % \
                  len(self.deferred)
        uc = self.context.uid_catalog
        nr_unsolved = [0, len(self.deferred)]
        while nr_unsolved[-1] > nr_unsolved[-2]:
            unsolved = []
            for d in self.deferred:
                src_obj = d['instance']
                src_field = d['field']
                old_uid = d['target_uid']
                target_uid = self.old2newuid[old_uid]
                try:
                    proxies = uc(UID=target_uid)
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
