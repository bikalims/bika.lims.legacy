""" Thermo Qtegra
"""
from string import digits
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter

class QtegraCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._column_header = []
        self._end_header = False
        self._column_header_stripped = None
        self.allowed_quan_types = ['ExtCal.Average', 'IntCal.Average']

    def _parseline(self, line):
        sline = line.split(';')
        if sline[2] in self.allowed_quan_types and not self._end_header:
            return 1
        elif sline > 0 and not self._end_header:
            self._column_header = sline[2:]
            self._column_header_stripped = [element[:-6].translate(None, digits) for element in self._column_header]
            self._end_header = True
            return 0
        elif sline > 0 and self._end_header:
            self.parse_line_data(sline)
        else:
            self.err("Unexpected format", numline=self._numline)
            return -1

    def parse_line_data(self, sline):

        resid = sline[1]
        analysis = {}
        for idx, result in enumerate(sline[2:]):
            if result != '':
                analysis[self._column_header_stripped[idx]] = {
                    'result': result,
                    'DefaultResult': 'result',
                }
        self._addRawResult(resid, analysis, False)
        return 0

class QtegraImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override, allowed_ar_states=None, allowed_analysis_states=None, instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context, idsearchcriteria, override, allowed_ar_states, allowed_analysis_states, instrument_uid)
