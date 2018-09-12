from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.fields import ExtReferenceField
from bika.lims.interfaces import ISampleType
from zope.component import adapts
from zope.interface import implements


class SampleTypeSchemaExtender(object):
    adapts(ISampleType)
    implements(IOrderableSchemaExtender)

    def __init__(self, context):
        self.context = context

    fields = [
        ExtReferenceField(
            'DefaultAnalysisSpecifications',
            required=0,
            allowed_types=('AnalysisSpec'),
            relationship='SampleTypeAnalysisSpec',
            referenceClass=HoldingReference,
            widget=ReferenceWidget(
                checkbox_bound = 0,
                label=_("Default Analysis Specification"),
                description=_("The Analysis Specification to set by default"),
                catalog_name='bika_setup_catalog',
                base_query={'review_state': 'active'},
                showOn=True,
            )
        ),
    ]

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
