# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from Products.Archetypes.public import StringWidget
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bhp.lims import bhpMessageFactory as _
from bhp.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationWidget
from bhp.lims.config import GENDERS_ANY
from bhp.lims.validators import AnalysisSpecificationsValidator
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.fields import ExtStringField
from bika.lims.interfaces import IAnalysisSpec
from zope.component import adapts
from zope.interface import implements


class AnalysisSpecsSchemaExtender(object):
    adapts(IAnalysisSpec)
    implements(IOrderableSchemaExtender)

    def __init__(self, context):
        self.context = context


    fields = [
        ExtStringField(
            "Gender",
            required=0,
            vocabulary=GENDERS_ANY,
            widget=SelectionWidget(
                format="select",
                label=_("Gender"),
            )
        ),
        ExtStringField(
            "Agefrom",
            required=0,
            widget=StringWidget(
                label=_("Age from (inclusive)"),
                description=_("Minimum age this specification will apply. "
                              "Inclusive value (>=). Format example: 15y 5m 6d"),
                maxlength=12,
                size=12,
            )
        ),
        ExtStringField(
            "Ageto",
            required=0,
            widget=StringWidget(
                label=_("Age to (inclusive)"),
                description=_("Maximum age this specification will apply. "
                              "Exclusive value (<). Format example: 85y 5m 6d"),
                maxlength=12,
                size=12,
            )
        ),
    ]

    def getOrder(self, schematas):
        default = schematas['default']
        default.remove('Gender')
        default.remove('Agefrom')
        default.remove('Ageto')
        default.insert(default.index('ResultsRange'), 'Gender')
        default.insert(default.index('ResultsRange'), 'Agefrom')
        default.insert(default.index('ResultsRange'), 'Ageto')
        schematas['default'] = default
        return schematas

    def getFields(self):
        return self.fields


class AnalysisSpecSchemaModifier(object):
    adapts(IAnalysisSpec)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        # Add panic alert range columns

        validator = AnalysisSpecificationsValidator()
        schema['ResultsRange'].subfields += ('minpanic', 'maxpanic')
        schema['ResultsRange'].subfield_validators['minpanic'] = validator
        schema['ResultsRange'].subfield_validators['maxpanic'] = validator
        schema['ResultsRange'].subfield_labels['minpanic'] = _('Min panic')
        schema['ResultsRange'].subfield_labels['maxpanic'] = _('Max panic')
        srcwidget = schema['ResultsRange'].widget
        schema['ResultsRange'].widget = AnalysisSpecificationWidget(
                    checkbox_bound=srcwidget.checkbox_bound,
                    label=srcwidget.label,
                    description=srcwidget.description,
        )
        return schema
