# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextAreaWidget
from Products.CMFCore.permissions import ModifyPortalContent, View
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bhp.lims.config import GENDERS
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields.proxyfield import ExtProxyField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.interfaces import IAnalysisRequest
from zope.component import adapts
from zope.interface import implements


class AnalysisRequestSchemaExtender(object):
    adapts(IAnalysisRequest)
    implements(IOrderableSchemaExtender)

    def __init__(self, context):
        self.context = context


    fields = [
        ExtProxyField(
            "ParticipantID",
            proxy="context.getSample()",
            mode="rw",
            required=1,
            widget=StringWidget(
                label=_("Participant ID"),
                maxlength=22,
                size=22,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            )
        ),

        ExtProxyField(
            "OtherParticipantReference",
            proxy="context.getSample()",
            mode="rw",
            required=0,
            widget=StringWidget(
                label=_("Other Participant Ref"),
                maxlength=12,
                size=12,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            )
        ),

        ExtProxyField(
            "ParticipantInitials",
            proxy="context.getSample()",
            mode="rw",
            required=1,
            widget=StringWidget(
                label=_("Participant Initials"),
                maxlength=2,
                size=2,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            )
        ),

        ExtProxyField(
            "Gender",
            proxy="context.getSample()",
            mode="rw",
            required=1,
            vocabulary= GENDERS,
            widget=SelectionWidget(
                format="radio",
                label=_("Gender"),
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            )
        ),

        ExtProxyField(
            "Visit",
            proxy="context.getSample()",
            mode="rw",
            required=1,
            widget=StringWidget(
                label=_("Visit Number"),
                maxlength=4,
                size=4,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            )
        ),

        ExtProxyField(
            "Fasting",
            proxy="context.getSample()",
            mode="rw",
            required=0,
            default=False,
            widget=BooleanWidget(
                format="radio",
                label=_("Fasting"),
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            ),
        ),

        ExtProxyField(
            'DateOfBirth',
            proxy="context.getSample()",
            mode="rw",
            required=1,
            widget=DateTimeWidget(
                label=_('Date of Birth'),
                datepicker_nofuture=1,
                show_time=False,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            ),
        ),

        ExtProxyField(
            "Volume",
            proxy="context.getSample()",
            mode="rw",
            required=1,
            widget=StringWidget(
                label=_("Volume"),
                maxlength=8,
                size=8,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            )
        ),

        ExtProxyField(
            "OtherInformation",
            proxy="context.getSample()",
            mode="rw",
            default_content_type="text/plain",
            allowable_content_types=("text/plain",),
            default_output_type="text/plain",
            widget=TextAreaWidget(
                label=_("Other relevant clinical information"),
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible'},
            ),
        ),

        ExtProxyField(
            "Courier",
            proxy="context.getSample()",
            required=0,
            allowed_types='Courier',
            relationship='AnalysisRequestCourier',
            mode="rw",
            read_permission=View,
            write_permission=ModifyPortalContent,
            widget=ReferenceWidget(
                label=_("Courier"),
                description=_("The person who delivered the sample"),
                render_own_label=True,
                visible={
                    'view': 'visible',
                    'edit': 'visible',
                    'add': 'invisible',
                    'header_table': 'visible',
                    'secondary':    'disabled',
                    'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                    'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                    'scheduled_sampling':{'view': 'invisible', 'edit': 'invisible'},
                    'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                    'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                    'sample_ordered':    {'view': 'invisible', 'edit': 'invisible'},
                    'sample_due':        {'view': 'visible', 'edit': 'visible'},
                    'sample_prep':       {'view': 'visible', 'edit': 'invisible'},
                    'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                    'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                    'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                    'verified':          {'view': 'visible', 'edit': 'invisible'},
                    'published':         {'view': 'visible', 'edit': 'invisible'},
                    'invalid':           {'view': 'visible', 'edit': 'invisible'},
                    'rejected':          {'view': 'visible', 'edit': 'invisible'},
                },
                catalog_name='portal_catalog',
                base_query={'review_state': 'active'},
                showOn=True,
            ),
        ),
    ]

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
