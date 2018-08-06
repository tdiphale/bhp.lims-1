# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

import os

from bhp.lims import api as _api
from bhp.lims.config import GENDERS
from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from openpyxl.reader.excel import load_workbook

_marker = object()
raw_specifcations = []


def get_specification_for(spec, default=_marker):
    """Returns a plain dictionary with specification values (min, max, etc.)
    It looks through an excel file provided as-is to find the record that
    better fits with the gender and age from the analysis request and for the
    analysis passed in
    :param: Analysis object or analysis uid or analysis brain
    """
    analysis = api.get_object_by_uid(spec.get(('analysis_uid')))

    if not analysis or not IRequestAnalysis.providedBy(analysis):
        if default is not _marker:
            return default
        api.fail("Type {} not supported: ".format(repr(analysis)))

    request = analysis.getRequest()
    gender = _api.get_field_value(request, "Gender")
    if not gender or gender.lower() not in GENDERS.keys():
        # If no gender is specified or not a valid value, assume any
        gender = 'a'

    dob = _api.get_field_value(request, "DateOfBirth")
    sampled = request.getDateSampled()
    if not dob or not sampled:
        if default is not _marker:
            return default
        api.fail("No DateSampled or Date of Birth set")

    specification = request.getSpecification()
    if not specification:
        # This should never happen, Since this function has been triggered, we
        # assume an specification has been set to the AR
        if default is not _marker:
            return default
        api.fail("Specification not set for request {}".format(request.id))

    sample_type = specification.getSampleTypeTitle()
    if not sample_type:
        if default is not _marker:
            return default
        api.fail("Sample Type not defined for specification {}".format(
            specification.Title()))

    years, months, days = _api.get_age(dob, sampled)
    return get_analysisspec(analysis_keyword=analysis.getKeyword(),
                             sample_type=sample_type, gender=gender,
                             years=years, months=months, days=days)


def get_analysisspec(analysis_keyword, sample_type, gender, years, months, days):
    """Returns a plain dictionary with specification values (min, max, etc.)
    that better suit with the parameters passed in.

    >>> specs = get_analysisspec("Cu", "Whole blood", "m", 0, 1, 0)
    >>> ' '.join([specs['min'], specs['max'], specs['minpanic'], specs['maxpanic'])
    10 20 5 25

    >>> specs = get_analysisspec("Cu", "Whole blood", "f", 0, 5, 0)
    >>> ' '.join([specs['min'], specs['max'], specs['minpanic'], specs['maxpanic'])
    20 30 15 35

    >>> specs = get_analysisspec("Cu", "Whole blood", "a", 0, 5, 0)
    >>> ' '.join([specs['min'], specs['max'], specs['minpanic'], specs['maxpanic'])
    30 40 25 45
    """
    if gender not in 'mf':
        gender = 'mf'

    def to_number(years, months, days):
        return int(days) + int(months)*30 + int(years)*30*12

    num_age = to_number(years, months, days)
    for spec in get_xls_specifications():
        if spec.get('keyword', None) != analysis_keyword:
            continue
        if spec.get('sample_type', None) != sample_type:
            continue
        sgender = spec.get('gender', 'mf')
        if gender not in sgender:
            continue

        age_low = spec.get('age_low', '0d')
        age_to = spec.get('age_to', '200y')
        y_from, m_from, d_from = _api.to_age(age_low)
        y_to, m_to, d_to = _api.to_age(age_to)

        num_from = to_number(y_from, m_from, d_from)
        num_to = to_number(y_to, m_to, d_to)
        if num_age >= num_from and num_age < num_to:
            return spec
    return {}


def get_xls_specifications():
    """Returns the specifications from the xlsx file"""
    worksheet_name = "Analysis Specifications"
    curr_dirname = os.path.dirname(os.path.abspath(__file__))
    filename = "{}/resources/results_ranges.xlsx".format(curr_dirname)
    workbook = load_workbook(filename=filename)
    worksheet = workbook.get_sheet_by_name("Analysis Specifications")
    if not worksheet:
        api.fail("Worksheet '{}' not found".format(worksheet_name))

    columns = []
    raw_specifications = list()
    for row in worksheet.rows:
        cell_values = map(lambda cell: cell.value, row)
        if not columns:
            columns = cell_values
            continue
        raw_specifications.append(dict(zip(columns, cell_values)))
    return raw_specifications


if __name__ == '__main__':
    raw_specifications = [
        {'keyword': 'Cu', 'age_from': '0m', 'age_to': '3m', 'gender': 'm',
         'min': 10, 'max': 20, 'minpanic': 5, 'maxpanic': 25},
        {'keyword': 'Cu', 'age_from': '3m', 'age_to': '6m', 'gender': 'm',
         'min': 20, 'max': 30, 'minpanic': 15, 'maxpanic': 35},
        {'keyword': 'Cu', 'age_from': '3m', 'age_to': '6m', 'gender': 'mf',
         'min': 30, 'max': 40, 'minpanic': 25, 'maxpanic': 45}
    ]
    import doctest
    doctest.testmod(raise_on_error=False,
                    optionflags=doctest.ELLIPSIS |
                                doctest.NORMALIZE_WHITESPACE)
