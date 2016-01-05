from bika.lims.browser import BrowserView
from bika.lims.interfaces import IBikaSetupType, ITransactionalType
from Products.Archetypes import Field
from Products.CMFCore.utils import getToolByName

import csv
import os
import shutil
import tempfile
import zipfile

ignore_fields = [
    # dublin
    'constrainTypesMode',
    'locallyAllowedTypes',
    'immediatelyAddableTypes',
    'subject',
    'relatedItems',
    'location',
    'language',
    'effectiveDate',
    'modification_date',
    'expirationDate',
    'creators',
    'contributors',
    'rights',
    'allowDiscussion',
    'excludeFromNav',
    'nextPreviousEnabled',
]


class Export(BrowserView):
    def __init__(self, context, request):
        super(Export, self).__init__(context, request)

        # We only store relative paths, the portal_path will be subbed out
        self.portal_path = '/'.join(self.portal.getPhysicalPath())

        # These are the catalogs which will be scanned for content
        # analysis catalog is not included! These will be exported
        # because they are reference targets.
        self.catalogs = ['portal_catalog',
                         'bika_catalog',
                         'bika_setup_catalog']

        # We'll keep open file descriptors and header listings here
        # rather than reopening and rediscovering them
        self.csvinfo = {}

    def __call__(self):
        """Export LIMS content to a zip file containing a bunch of CSV files.
        Any attachments, files, images, will also be included.
        """

        self.tempdir = tempfile.mkdtemp()

        # Laboratory and BikaSetup, we will handle these manually.
        self.export_laboratory()
        self.export_bika_setup()

        # All other types flagged with IBikaSetupType or ITransactionalType
        # will be exported now:
        if 'bika_setup_types' in self.request.form:
            self.export_content('bika.lims.interfaces.IBikaSetupType')
        if 'bika_transactional_types' in self.request.form:
            self.export_content('bika.lims.interfaces.ITransactionalType')

        zfn = self.create_zipfile()

        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length', os.stat(zfn).st_size)
        setheader('Content-Type', 'application/zip')
        setheader('Content-Disposition', 'inline; filename=bikalims.zip')
        self.request.RESPONSE.write(open(zfn, 'rb').read())

    def export_laboratory(self):
        """Write the laboratory data in non-standard CSV format:
        First column is field names, second column is field values.
        """
        instance = self.portal.bika_setup.laboratory
        fields = self.get_fields(instance.schema)
        fn = os.path.join(self.tempdir, 'Laboratory.csv')
        with open(fn, mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['field', 'value'])
            for field in fields:
                writer.writerow([field.getName(), self.mutate(instance, field)])

    def export_bika_setup(self):
        """Write the BikaSetup field data in non-standard CSV format:
        First column is field names, second column is field values.
        """
        instance = self.portal.bika_setup
        fields = self.get_fields(instance.schema)
        fn = os.path.join(self.tempdir, 'Laboratory.csv')
        with open(fn, mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['field', 'value'])
            for field in fields:
                writer.writerow([field.getName(), self.mutate(instance, field)])

    def export_content(self, interface):
        """Scan for and export objects implementing 'interface'
        """
        for catalog in self.catalogs:
            catalog = self.portal[catalog]
            for brain in catalog(object_provides=interface):
                self.contenttype_write_values(brain)

    def contenttype_write_values(self, brain):
        """Write field values for the specified object into CSV file
        """
        instance = brain.getObject()
        portal_type = instance.portal_type
        # check that the csv and headers are initialised for this type
        self.contenttype_init_csv(instance)
        path = '/'.join(instance.getPhysicalPath()[:-1])
        # path and uid are required values
        values = [path.replace(self.portal_path, ''),
                  instance.UID()]
        # then collect up schema field values
        fields = self.csvinfo[portal_type]['fields']
        for field in fields:
            values.append(self.mutate(instance, field))
        # and write them away.
        writer = self.csvinfo[portal_type]['writer']
        writer.writerow(values)

    def contenttype_init_csv(self, instance):
        """Create the file descriptor and headers list for the
        contenttype of instance.  This is used only for actual portal_type
        objects.
        """
        portal_type = instance.portal_type
        fields = self.get_fields(instance.schema)
        headers = ['path', 'uid'] + [f.getName() for f in fields]
        if portal_type not in self.csvinfo:
            fn = os.path.join(self.tempdir, portal_type + '.csv')
            fd = open(fn, mode='w')
            writer = csv.writer(fd)
            self.csvinfo[portal_type] = {
                'file': fd,
                'writer': writer,
                'headers': headers,
                'fields': fields,
            }
            writer.writerow(headers)

    def dictfield_write_values(self, instance, field):
        """This is called when a field with a dictionary value (or list of
        dicts) is passed through self.mutate().
        """
        # we are guaranteed that at least one dict is present at this point
        fieldvalue = field.get(instance)
        # Could be dict, or list of dicts, we don't want to care:
        if type(fieldvalue) == dict:
            fieldvalue = [fieldvalue]
        # store the keys so that the ordering remains the same
        keys = list(fieldvalue[0].keys())
        headers = ['instance_uid', 'instance_id'] + keys
        # check that the csv and headers are initialised for this field
        self.dictfield_init_csv(instance, field, headers)
        # fnkey is for identifying our csv from self.csvinfo
        fnkey = '%s_%s' % (instance.portal_type, field.getName())
        writer = self.csvinfo[fnkey]['writer']
        for value in fieldvalue:
            # I don't care about dictionaries without any values
            if not any(value.values()):
                break
            # source instance identifiers
            rowvalues = [instance.UID(), instance.id]
            for key in keys:
                rowvalues.append(value.get(key, ''))
            # write away the row
            writer.writerow(rowvalues)

    def dictfield_init_csv(self, instance, field, headers):
        """Create the file descriptor and headers list for field values
        which are dictionaries or lists of dictionaries.
        """
        portal_type = instance.portal_type
        fieldname = field.getName()
        fnkey = '%s_%s' % (portal_type, fieldname)
        if fnkey not in self.csvinfo:
            fn = os.path.join(self.tempdir, fnkey + '.csv')
            fd = open(fn, mode='w')
            writer = csv.writer(fd)
            self.csvinfo[fnkey] = {
                'file': fd,
                'writer': writer,
                'headers': headers,
            }
            writer.writerow(headers)

    def reference_write_values(self, instance, field):
        """This is called when a multiValued reference field is
        passed through self.mutate().
        """
        values = field.get(instance)
        # check that the csv and headers are initialised for this field
        self.reference_init_csv(field)
        writer = self.csvinfo[field.relationship]['writer']
        for value in values:
            # ['source_uid', 'source_id', 'target_uid', 'target_id']
            rowvalues = [instance.UID(), instance.id, value.UID(), value.id]
            writer.writerow(rowvalues)

    def reference_init_csv(self, field):
        """Create the file descriptor and headers list for multiValued
        reference fields
        """
        headers = ['source_uid', 'source_id', 'target_uid', 'target_id']
        if field.relationship not in self.csvinfo:
            fn = os.path.join(self.tempdir, field.relationship + '.csv')
            fd = open(fn, mode='w')
            writer = csv.writer(fd)
            self.csvinfo[field.relationship] = {
                'file': fd,
                'writer': writer,
                'headers': headers,
            }
            writer.writerow(headers)

    def get_fields(self, schema):
        """Return a simple list of fields.
        Exclude ignored and computed fields.
        """
        fields = []
        for field in schema.fields():
            if field.getName() in ignore_fields:
                continue
            if Field.IComputedField.providedBy(field):
                continue
            fields.append(field)
        return fields

    def get_extension(self, mimetype):
        """Return first extension for mimetype, if any is found.
        If no extension found, return ''
        """
        mr = getToolByName(self.portal, "mimetypes_registry")
        extension = ''
        for ext, mt in mr.extensions.items():
            if mimetype == mt:
                extension = ext
        return extension

    def create_zipfile(self):
        # close all open files in self.csvinfo...
        for v in self.csvinfo.values():
            v['file'].close()
        # Create zip file
        tmpfile = tempfile.mktemp(suffix='.zip')
        z = zipfile.ZipFile(tmpfile, 'w', zipfile.ZIP_DEFLATED)
        # toss all the files into the zip
        for fname in os.listdir(self.tempdir):
            z.write(os.path.join(self.tempdir, fname), fname)
        z.close()
        return tmpfile

    def mutate(self, instance, field):
        value = field.get(instance)
        # Booleans are special; we'll return them as '1' or ''.
        if type(value) == bool:
            return '1' if value else ''
        # Zero is special: it's false-ish, but the value is important.
        if value is 0:
            return 0
        # Other falsish values make empty strings.
        if not value:
            return ''
        # Date fields get stringed to rfc8222
        if Field.IDateTimeField.providedBy(field):
            return value.rfc822() if value else None
        # TextField implements IFileField (wtf), so we must handle it
        # before IFileField. It's just returned verbatim.
        elif Field.ITextField.providedBy(field):
            return value
        # Files get saved into tempdir, and the returned value is
        # the filename with no path.
        elif Field.IFileField.providedBy(field):
            # except empty files of course.
            if not value.size:
                return ''
            extension = self.get_extension(value.content_type)
            # The filename will be munged slightly to prevent duplications.
            fn = instance.id + '__' + field.getName() + \
                 '__' + value.filename + extension
            of = open(os.path.join(self.tempdir, fn), 'wb')
            of.write(value.data)
            of.close()
            return fn
        elif Field.IReferenceField.providedBy(field):
            if field.multiValued:
                # multiValued reference fields get their own special CSV
                return self.reference_write_values(instance, field)
            else:
                # singleValued references just take the uid for
                # identification of the target
                return value.UID()
        elif Field.ILinesField.providedBy(field):
            return "\n".join(value)
        # depend on value of field, to decide mutation.
        else:
            value = field.get(instance)
            # Dictionaries or lists of dictionaries
            if type(value) == dict \
                    or (type(value) in (list, tuple)
                        and type(value[0]) == dict):
                return self.dictfield_write_values(instance, field)
            else:
                return value
