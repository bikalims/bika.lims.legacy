from bika.lims.exportimport.instruments.resultsimport import InstrumentResultsFileParser, AnalysisResultsImporter
import re


class TC20TXTParser(InstrumentResultsFileParser):

    def __init__(self, txt, analysiskey, mimetype='text'):
        InstrumentResultsFileParser.__init__(self, txt, mimetype)
        self.analysiskey = analysiskey
        self._mimetype = mimetype

    def calculate(self, vals):
        #print vals
        if type(vals) == str:
            vals = vals.replace('^', 'E')
            vals_list = vals.split('x')
            if len(vals_list) == 2:
                return float(vals_list[0]) * float(vals_list[1])

        return float(vals)

    def parse(self):
        infile = self.getInputFile()
        self.log("Parsing file ${file_name}", mapping={"file_name": infile.filename})
        with open(infile.name, 'rU') as input_file:
            sub = ''
            for line in input_file:
                sub += line.lstrip()
        results = sub.split('%')

        for result in results:
                raw_result = {}

                rid = re.findall('\sSample:\s(\S+)', result)
                frid = rid[0] if len(rid) > 0 else ''

                tc_count = re.findall('\sTotal cell count:\s(\S+)', result)
                ftc_count = tc_count[0] if len(tc_count) > 0 else 0

                lc_count = re.findall('\sLive cell count:\s(\S+)', result)
                flc_count = lc_count[0] if len(lc_count) > 0 else 0

                live_cells = re.findall('\sLive cells:\s([0-9]+)', result)
                flive_cells = live_cells[0] if len(live_cells) > 0 else 0
                gated_count = 'N'
                if re.search('Gated count', result):
                    gated_count = 'Y'

                if self.analysiskey == 'TCC':
                    raw_result[self.analysiskey] = {
                        'Request ID': frid,
                        'Tcc': self.calculate(ftc_count),
                        'Lcc': self.calculate(flc_count),
                        'Lvc': flive_cells,
                        #'Gated Count': gated_count
                    }
                if len(frid) > 0:
                    self._addRawResult(frid, raw_result)


class TC20Importer(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):

        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)