# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from datetime import datetime

from Products.ATContentTypes.utils import DT2dt
from bhp.lims import api
from bika.lims.browser.analysisrequest.publish import \
    AnalysisRequestPublishView as _AnalysisRequestPublishView

_marker = object()


class AnalysisRequestPublishView(_AnalysisRequestPublishView):

    def __call__(self):
        return super(AnalysisRequestPublishView, self).__call__()

    def get(self, instance, field_name, default=_marker):
        return api.get_field_value(instance, field_name, default)

    def get_age(self, instance):
        splitted = self.get_age_splitted(instance)
        year = splitted.get('year') or ''
        month = splitted.get('month') or ''
        day = splitted.get('day') or ''
        arr = [
            year and '{}y'.format(year) or '',
            month and '{}m'.format(month) or '',
            day and '{}d'.format(day) or '',
        ]
        return ' '.join(arr)

    def get_age_splitted(self, instance):
        dob = self.get(instance, 'DateOfBirth', None)
        if not dob:
            return dict(year=0, month=0, day=0)

        dob = DT2dt(dob).replace(tzinfo=None)
        now = datetime.today()

        currentday = now.day
        currentmonth = now.month
        currentyear = now.year
        birthday = dob.day
        birthmonth = dob.month
        birthyear = dob.year
        ageday = currentday - birthday
        months31days = [1, 3, 5, 7, 8, 10, 12]

        if ageday < 0:
            currentmonth -= 1
            if currentmonth < 1:
                currentyear -= 1
                currentmonth = currentmonth + 12

            dayspermonth = 30
            if currentmonth in months31days:
                dayspermonth = 31
            elif currentmonth == 2:
                dayspermonth = 28
                if(currentyear % 4 == 0
                   and (currentyear % 100 > 0 or currentyear % 400 == 0)):
                    dayspermonth += 1

            ageday = ageday + dayspermonth

        agemonth = currentmonth - birthmonth
        if agemonth < 0:
            currentyear -= 1
            agemonth = agemonth + 12

        ageyear = currentyear - birthyear

        return dict(year=ageyear, month=agemonth, day=ageday)
