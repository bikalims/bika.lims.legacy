# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from ajax import ReferenceWidgetVocabulary
from ajax import ajaxGetClientInfo
from views.analysisprofiles import ClientAnalysisProfilesView
from views.analysisrequests import ClientAnalysisRequestsView
from views.analysisrequests import ClientBatchAnalysisRequestsView
from views.analysisspecs import ClientAnalysisSpecsView
from views.analysisspecs import SetSpecsToLabDefaults
from views.artemplates import ClientARTemplatesView
from views.attachments import ClientAttachmentsView
from views.batches import ClientBatchesView
from views.contacts import ClientContactVocabularyFactory
from views.contacts import ClientContactsView
from views.orders import ClientOrdersView
from views.samplepoints import ClientSamplePointsView
from views.samples import ClientSamplesView
from views.samplingrounds import ClientSamplingRoundsView
from views.srtemplates import ClientSamplingRoundTemplatesView
from workflow import ClientWorkflowAction

