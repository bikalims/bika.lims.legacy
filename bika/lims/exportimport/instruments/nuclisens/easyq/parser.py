from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentXLSXResultsFileParser


class EasyQXLSXParser(InstrumentXLSXResultsFileParser):
    def __init__(self, xlsx):
        InstrumentXLSXResultsFileParser.__init__(self, xlsx)
        self.columns = []
        self.resid = ''
        self.head_done = False

    def _parse_row(self, row_list):

        if row_list[0] == 'Version' and not self.head_done:
            self.columns = row_list
            self.head_done = True
            return 0

        # if we already have the headers and the list has
        # the correct no of elements then parse it
        elif len(row_list) == len(self.columns) and self.head_done:
            
            rawdict = {}
            for i, red in enumerate(row_list):
                rawdict[self.columns[i]] = red
            
            if row_list['Severity']== 'Info':
                #if the severity is "Info" the line does not contain actual result
                return 0
            testname = row_list['Description']
            if testname=="":
                self.err("test not specified ")
                return -1
            # default result added as the AU block of the file as
            # suggested by lemoene
            rawdict['DefaulResult'] = 'Value'

            # We should remove any unit from the result; these are already
            # completed as part of the AnalysisService configuration.
            if rawdict['Value'].find('/') > -1:
                parts = rawdict['Value'].split()
                rawdict['Value'] = ' '.join(parts[:-1])

            self.resid = rawdict['SampleID']
            if self.resid == '':
                self.resid = rawdict['SerialNumber']
                if self.resid == '':
                    self.err('result identification not found')
                    return -1

            self._addRawResult(self.resid, {testname: rawdict}, False)
            return 0
        else:
            self.err('unexpected data format')
            return -1
