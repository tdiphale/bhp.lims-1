# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from archetypes.schemaextender.interfaces import ISchemaModifier
from bhp.lims import bhpMessageFactory as _
from bhp.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationWidget
from bhp.lims.validators import AnalysisSpecificationsValidator
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysisSpec
from zope.component import adapts
from zope.interface import implements

class AnalysisSpecSchemaModifier(object):
    adapts(IAnalysisSpec)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        # Add panic alert range columns

        validator = AnalysisSpecificationsValidator()
        schema['ResultsRange'].subfields += ('minpanic', 'maxpanic', 'calculation')
        schema['ResultsRange'].subfield_validators['minpanic'] = validator
        schema['ResultsRange'].subfield_validators['maxpanic'] = validator
        schema['ResultsRange'].subfield_labels['minpanic'] = _('Min panic')
        schema['ResultsRange'].subfield_labels['maxpanic'] = _('Max panic')
        schema['ResultsRange'].subfield_labels['calculation'] = _("Specification calculation")
        srcwidget = schema['ResultsRange'].widget
        schema['ResultsRange'].widget = AnalysisSpecificationWidget(
                    checkbox_bound=srcwidget.checkbox_bound,
                    label=srcwidget.label,
                    description=srcwidget.description,
        )
        return schema
