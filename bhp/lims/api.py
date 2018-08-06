# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
import re

from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from bika.lims import api as bapi
from dateutil.relativedelta import relativedelta

_marker = object()


def get_field_value(instance, field_name, default=_marker):
    """Returns the value of a Schema field from the instance passed in
    """
    instance = bapi.get_object(instance)
    field = instance.Schema() and instance.Schema().getField(field_name) or None
    if not field:
        if default is not _marker:
            return default
        bapi.fail("No field {} found for {}".format(field_name, repr(instance)))
    return instance.Schema().getField(field_name).get(instance)


def get_age(datetime_from, datetime_to=None):
    """Returns the elapsed time in years, months and days between the two
    dates passed in."""
    if not datetime_to:
        datetime_to = DateTime()

    if not bapi.is_date(datetime_from) or not bapi.is_date(datetime_to):
        bapi.fail("Only DateTime and datetype types are supported")


    dfrom = DT2dt(bapi.to_date(datetime_from)).replace(tzinfo=None)
    dto = DT2dt(bapi.to_date(datetime_to)).replace(tzinfo=None)

    diff = relativedelta(dto, dfrom)
    return (diff.years, diff.months, diff.days)


def to_age_str(years=0, months=0, days=0):
    """Returns a string representation of an age
    """
    if not bapi.is_floatable(years):
        bapi.fail("Years are not floatable")
    if not bapi.is_floatable(months):
        bapi.fail("Months are not floatabla")
    if not bapi.is_floatable(days):
        bapi.fail("Days are not floatable")

    age_arr = list()
    if years:
        age_arr.append("{}y".format(years))
    if months:
        age_arr.append("{}m".format(months))
    if days:
        age_arr.append("{}d".format(days))
    return ' '.join(age_arr)


def to_age(age):
    """Returns  a tuple with the year, month and days for a given age in passed
    in as string format
    """
    def get_age_value(age_str, age_key):
        regex = '(\d+){}'.format(age_key)
        matches = re.findall(regex, age)
        if not matches:
            return 0
        age_val = matches[0]
        if age_val and bapi.is_floatable(age_val):
            return age_val.strip()
        return 0

    years = get_age_value(age, 'y')
    months = get_age_value(age, 'm')
    days = get_age_value(age, 'd')
    return (years, months, days)
