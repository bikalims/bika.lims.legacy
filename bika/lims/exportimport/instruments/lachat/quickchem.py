# -*- coding: utf-8 -*-
""" Lachat QuickChem FIA
"""
import re
import csv
import logging

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

logger = logging.getLogger(__name__)

title = "Lachat QuickChem FIA"


class Parser(InstrumentResultsFileParser):
    """ Instrument Parser
    """
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'CSV')

    def parse(self):
        """ CSV Parser
        """

        reader = csv.reader(self.getInputFile(), dialect='excel')

        for n, row in enumerate(reader):

            # prepare the rawdict
            rawdict = {}
            for n, value in enumerate(row):
                rawdict["Column_%d" % n] = value

            # parse the second value for the result id, e.g. '[A00035640001] K04'
            parsed = re.search('(\[(.*)\])\ (.*)', row[1])

            if parsed is None:
                self.err("Result identification not found.", numline=n)
                continue

            resid = parsed.group(2)

            # Service Keyword
            service = parsed.group(3)

            rawdict['Service'] = service
            rawdict['DefaultResult'] = 'Column_4'

            self._addRawResult(resid, values={service: rawdict}, override=False)

        self.log(
            "End of file reached successfully: ${total_objects} objects, "
            "${total_analyses} analyses, ${total_results} results",
            mapping={"total_objects": self.getObjectsTotalCount(),
                     "total_analyses": self.getAnalysesTotalCount(),
                     "total_results": self.getResultsTotalCount()}
        )

        return True


class Importer(AnalysisResultsImporter):
    """ Instrument Importer
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
    infile = request.form['lachat_quickchem_fia_file']
    fileformat = request.form['lachat_quickchem_fia_format']
    artoapply = request.form['lachat_quickchem_fia_artoapply']
    override = request.form['lachat_quickchem_fia_override']
    sample = request.form.get('lachat_quickchem_fia_sample', 'requestid')
    instrument = request.form.get('lachat_quickchem_fia_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
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
