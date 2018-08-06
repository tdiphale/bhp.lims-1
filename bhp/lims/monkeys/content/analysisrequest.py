# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from bika.lims import api
from bika.lims.content.analysisspec import ResultsRangeDict

def getResultsRange(self):
    """Returns the valid result ranges for the analyses this Analysis
    Request contains.

    By default uses the result ranges defined in the Analysis Specification
    set in "Specification" field if any. Values manually set through
    `ResultsRange` field for any given analysis keyword have priority over
    the result ranges defined in "Specification" field.

    :return: A list of dictionaries, where each dictionary defines the
        result range to use for any analysis contained in this Analysis
        Request for the keyword specified. Each dictionary has, at least,
            the following keys: "keyword", "min", "max"
    :rtype: dict
    """
    specs_range = []
    specification = self.getSpecification()
    if specification:
        specs_range = specification.getResultsRange()
        specs_range = specs_range and specs_range or []

    # Override with AR's custom ranges
    ar_range = self.Schema().getField("ResultsRange").get(self)
    if not ar_range:
        return specs_range

    # Remove those analysis ranges that neither min nor max are floatable
    an_specs = [an for an in ar_range if
                api.is_floatable(an.get('min', None)) or
                api.is_floatable(an.get('max', None))]
    # Want to know which are the analyses that needs to be overriden
    keywords = map(lambda item: item.get('keyword'), an_specs)
    # Get rid of those analyses to be overriden
    out_specs = [sp for sp in specs_range if sp['keyword'] not in keywords]
    # Add manually set ranges
    out_specs.extend(an_specs)
    # return a list of ResultRangeDict objects
    return map(lambda spec: ResultsRangeDict(spec), out_specs)
