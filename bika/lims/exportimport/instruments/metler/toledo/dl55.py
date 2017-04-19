# -*- coding: utf-8 -*-
""" Metler Toledo DL55
"""
import json
import re
import traceback

from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims.utils import t
from openpyxl import load_workbook

title = "Metler Toledo DL55"


class Parser(InstrumentResultsFileParser):
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'XLSX')

    def parse(self):
        """ parse the data
        """

        wb = load_workbook(self.getInputFile())
        sheet = wb.worksheets[0]

        sample_id = None
        for row in sheet.rows:

            # sampleid is only present in first row of each sample.
            # any rows above the first sample id are ignored.
            if row[1].value:
                sample_id = row[1].value
            if not sample_id:
                continue

            # keyword is stripped of non-word characters
            keyword = re.sub(r"\W", "", row[6].value)

            # result is floatable or error
            result = row[4].value
            try:
                float(result)
            except ValueError:
                self.log(
                    "Error in sample '" + sample_id + "': " + "Result for '" +
                    keyword + "' is not a number " + "(" + result + ").")
                continue

            # Compose dict for importer.  No interim values, just a result.
            rawdict = {
                'DefaultResult': 'Result',
                'Result': result,
            }
            self._addRawResult(sample_id,
                               values={keyword: rawdict},
                               override=False)
        return True


class Importer(AnalysisResultsImporter):
    """ Importer
    """

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,
                                         idsearchcriteria,
                                         override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def Import(context, request):
    """ Import Form
    """
    infile = request.form['metler_toledo_dl55_file']
    fileformat = request.form['metler_toledo_dl55_format']
    artoapply = request.form['metler_toledo_dl55_artoapply']
    override = request.form['metler_toledo_dl55_override']
    sample = request.form.get('metler_toledo_dl55_sample', 'requestid')
    instrument = request.form.get('metler_toledo_dl55_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'xlsx':
        parser = Parser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Load the importer
        status = ['sample_received', 'attachment_due', 'to_be_verified']
        if artoapply == 'received':
            status = ['sample_received']
        elif artoapply == 'received_tobeverified':
            status = ['sample_received', 'attachment_due', 'to_be_verified']

        over = [False, False]
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]

        sam = ['getRequestID', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getRequestID']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        importer = Importer(parser=parser,
                            context=context,
                            idsearchcriteria=sam,
                            allowed_ar_states=status,
                            allowed_analysis_states=None,
                            override=over,
                            instrument_uid=instrument)
        tbex = ''
        try:
            importer.process()
        except:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)
