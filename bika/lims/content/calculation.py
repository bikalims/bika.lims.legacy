# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import re
import sys
import math

import transaction
from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import registerType
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

# Fields
from Products.Archetypes.atapi import TextField
from Products.ATExtensions.field import RecordsField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import HistoryAwareReferenceField

# Widgets
from Products.Archetypes.atapi import ReferenceWidget
from Products.Archetypes.atapi import TextAreaWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget

# bika.lims imports
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import ICalculation
from bika.lims.content.bikaschema import BikaSchema


schema = BikaSchema.copy() + Schema((

    InterimFieldsField(
        'InterimFields',
        widget=BikaRecordsWidget(
            label=_("Calculation Interim Fields"),
            description=_(
                "Define interim fields such as vessel mass, dilution factors, "
                "should your calculation require them. The field title "
                "specified here will be used as column headers and field "
                "descriptors where the interim fields are displayed. If "
                "'Apply wide' is enabled the field will be shown in a "
                "selection box on the top of the worksheet, allowing to apply "
                "a specific value to all the corresponding fields on the "
                "sheet."),
        )
    ),

    HistoryAwareReferenceField(
        'DependentServices',
        required=1,
        multiValued=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('AnalysisService',),
        relationship='CalculationAnalysisService',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            visible=False,
            label=_("Dependent Analyses"),
        ),
    ),

    TextField(
        'Formula',
        validators=('formulavalidator',),
        default_content_type='text/plain',
        allowable_content_types=('text/plain',),
        widget=TextAreaWidget(
            label=_("Calculation Formula"),
            description=_(
                "<p>The formula you type here will be dynamically calculated "
                "when an analysis using this calculation is displayed.</p>"
                "<p>To enter a Calculation, use standard maths operators,  "
                "+ - * / ( ), and all keywords available, both from other "
                "Analysis Services and the Interim Fields specified here, "
                "as variables. Enclose them in square brackets [ ].</p>"
                "<p>E.g, the calculation for Total Hardness, the total of "
                "Calcium (ppm) and Magnesium (ppm) ions in water, is entered "
                "as [Ca] + [Mg], where Ca and MG are the keywords for those "
                "two Analysis Services.</p>"),
        )
    ),

    RecordsField(
        'TestParameters',
        required=False,
        subfields=('keyword', 'value'),
        subfield_labels={'keyword': _('Keyword'), 'value': _('Value')},
        subfield_readonly={'keyword': True, 'value': False},
        subfield_types={'keyword': 'string', 'value': 'float'},
        default=[{'keyword': '', 'value': 0}],
        widget=RecordsWidget(
            label=_("Test Parameters"),
            description=_("To test the calculation, enter values here for all "
                          "calculation parameters.  This includes Interim "
                          "fields defined above, as well as any services that "
                          "this calculation depends on to calculate results."),
            allowDelete=False,
        ),
    ),

    TextField(
        'TestResult',
        default_content_type='text/plain',
        allowable_content_types=('text/plain',),
        widget=TextAreaWidget(
            label=_('Test Result'),
            description=_("The result after the calculation has taken place "
                          "with test values.  You will need to save the "
                          "calculation before this value will be calculated."),
        )
    ),

))

schema['title'].widget.visible = True
schema['description'].widget.visible = True


class Calculation(BaseFolder, HistoryAwareMixin):
    """Calculation for Analysis Results
    """
    implements(ICalculation)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def setInterimFields(self, value):
        new_value = []

        for x in range(len(value)):
            row = dict(value[x])
            keys = row.keys()
            if 'value' not in keys:
                row['value'] = 0
            new_value.append(row)

        self.getField('InterimFields').set(self, new_value)

    def setFormula(self, Formula=None):
        """Set the Dependent Services from the text of the calculation Formula
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        if Formula is None:
            self.setDependentServices(None)
            self.getField('Formula').set(self, Formula)
        else:
            DependentServices = []
            keywords = re.compile(r"\[([^\.^\]]+)\]").findall(Formula)
            for keyword in keywords:
                service = bsc(portal_type="AnalysisService",
                              getKeyword=keyword)
                if service:
                    DependentServices.append(service[0].getObject())

            self.getField('DependentServices').set(self, DependentServices)
            self.getField('Formula').set(self, Formula)

    def getMinifiedFormula(self):
        """Return the current formula value as text.
        The result will have newlines and additional spaces stripped out.
        """
        value = " ".join(self.getFormula().splitlines())
        return value

    def getCalculationDependencies(self, flat=False, deps=None):
        """ Recursively calculates all dependencies of this calculation.
            The return value is dictionary of dictionaries (of dictionaries....)

            {service_UID1:
                {service_UID2:
                    {service_UID3: {},
                     service_UID4: {},
                    },
                },
            }

            set flat=True to get a simple list of AnalysisService objects
        """
        if deps is None:
            deps = [] if flat is True else {}

        for service in self.getDependentServices():
            calc = service.getCalculation()
            if calc:
                calc.getCalculationDependencies(flat, deps)
            if flat:
                deps.append(service)
            else:
                deps[service.UID()] = {}
        return deps

    def getCalculationDependants(self):
        """Return a flat list of services who's calculations depend on this."""
        deps = []
        for service in self.getBackReferences('AnalysisServiceCalculation'):
            calc = service.getCalculation()
            if calc and calc.UID() != self.UID():
                calc.getCalculationDependants(deps)
            deps.append(service)
        return deps

    def setTestParameters(self, form_value):
        """This is called from the objectmodified subscriber, to ensure
        correct population of the test-parameters field.
        It collects Keywords for all services that are direct dependencies of
        this calculatioin, and all of this calculation's InterimFields,
        and gloms them together.
        """
        params = []

        # Set default/existing values for InterimField keywords
        for interim in self.getInterimFields():
            keyword = interim['keyword']
            ex = [x['value'] for x in form_value if x['keyword'] == keyword]
            params.append({'keyword': keyword,
                          'value': ex[0] if ex else interim['value']})
        # Set existing/blank values for service keywords
        for service in self.getDependentServices():
            keyword = service.getKeyword()
            ex = [x['value'] for x in form_value if x['keyword'] == keyword]
            params.append({'keyword': keyword,
                          'value': ex[0] if ex else ''})
        self.Schema().getField('TestParameters').set(self, params)

    def setTestResult(self, form_value):
        """Calculate formula with TestParameters and enter result into
         TestResult field.
        """
        # Create mapping from TestParameters
        mapping = {x['keyword']: x['value'] for x in self.getTestParameters()}
        # Gather up and parse formula
        formula = self.getMinifiedFormula()
        formula = formula.replace('[', '{').replace(']', '}').replace('  ', '')
        result = 'Failure'

        try:
            # print "pre: {}".format(formula)
            formula = formula.format(**mapping)
            # print "formatted: {}".format(formula)
            result = eval(formula, {"__builtins__": None, 'math': math})
            # print "result: {}".format(result)
        except TypeError as e:
            # non-numeric arguments in interim mapping?
            result = "TypeError: {}".format(str(e.args[0]))
        except ZeroDivisionError as e:
            result = "Division by 0: {}".format(str(e.args[0]))
        except KeyError as e:
            result = "Key Error: {}".format(str(e.args[0]))
        except Exception as e:
            result = "Unspecified exception: {}".format(str(e.args[0]))
        self.Schema().getField('TestResult').set(self, str(result))

    def workflow_script_activate(self):
        wf = getToolByName(self, 'portal_workflow')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be re-activated if services it depends on
        # are deactivated.
        services = self.getDependentServices()
        inactive_services = []
        for service in services:
            if wf.getInfoFor(service, "inactive_state") == "inactive":
                inactive_services.append(service.Title())
        if inactive_services:
            msg = _("Cannot activate calculation, because the following "
                    "service dependencies are inactive: ${inactive_services}",
                    mapping={'inactive_services': safe_unicode(", ".join(inactive_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException

    def workflow_script_deactivate(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be deactivated if active services are using it.
        services = bsc(portal_type="AnalysisService", inactive_state="active")
        calc_services = []
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.UID() == self.UID():
                calc_services.append(service.Title())
        if calc_services:
            msg = _('Cannot deactivate calculation, because it is in use by the '
                    'following services: ${calc_services}',
                    mapping={'calc_services': safe_unicode(", ".join(calc_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException


registerType(Calculation, PROJECTNAME)
