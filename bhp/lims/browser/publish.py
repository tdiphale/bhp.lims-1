# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from datetime import datetime

from Products.ATContentTypes.utils import DT2dt
from bhp.lims import api
from bhp.lims.api import get_field_value
from bika.lims.browser.analysisrequest.publish import \
    AnalysisRequestPublishView as _AnalysisRequestPublishView

_marker = object()


class AnalysisRequestPublishView(_AnalysisRequestPublishView):

    def __call__(self):
        return super(AnalysisRequestPublishView, self).__call__()

    def get(self, instance, field_name, default=_marker):
        return api.get_field_value(instance, field_name, default)

    def get_age(self, instance):
        dob = get_field_value(instance, "DateOfBith")
        sampled = instance.getDateSampled()
        if not dob or not sampled:
            return ''

        year, month, days = api.get_age(dob, sampled)
        arr = [
            year and '{}y'.format(year) or '',
            month and '{}m'.format(month) or '',
            days and '{}d'.format(days) or '',
        ]
        return ' '.join(arr)
