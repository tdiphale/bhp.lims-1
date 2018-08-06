# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFPlone.i18nl10n import ulocalized_time
import json


class VolumeUnitWidget(TypesWidget):
    security = ClassSecurityInfo()
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bhp_widgets/volumeunitwidget",
    })

    @security.public
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        field_name = field.getName()

        def get_value(subfield, empty_marker=None):
            subfield_name = "{}_{}".format(field_name, subfield)
            return form.get(subfield_name, empty_marker)

        outvalues = [{'noa': get_value('noa', '0'),
                      'volume': get_value('volume', empty_marker),
                      'unit': get_value('unit', empty_marker)}]
        return outvalues, {}


registerWidget(VolumeUnitWidget, title='VolumeUnitWidget',
               description=('Simple control with volume and input fields'),
               )
