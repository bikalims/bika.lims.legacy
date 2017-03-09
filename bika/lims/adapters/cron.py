from collective.cron import crontab
from datetime import datetime
from plone import api
class ExpireReferenceSamples(crontab.Runner):
    def run(self):
        try:
            workflow = api.portal.get_tool('portal_workflow')
            bc = api.portal.get_tool('bika_catalog')
            query = {'portal_type': 'ReferenceSample',
                     'getExpiryDate': {'query': datetime.today(), 'range': 'max'},
                     'review_state': 'current',
                    }
            brains = bc(query)
            for brain in brains:
                workflow.doActionFor(brain.getObject(), 'expire')

        except Exception, e:
            raise
