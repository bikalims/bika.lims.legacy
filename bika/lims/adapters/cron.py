from collective.cron import crontab
from datetime import datetime
class ExpireReferenceSamples(crontab.Runner):
    def run(self):
        print '******************************************************'
        bc = api.portal.get_tool('bika_catalog')
        query = {'portal_type': 'ReferenceSample',
                'getExpiryDate': {'query': datetime.today(), 'range': 'max'}}
        brains = bc(query)
        print '******************************************************'
