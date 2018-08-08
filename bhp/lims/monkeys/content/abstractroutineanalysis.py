# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from bika.lims import api
from bika.lims.content.analysisspec import ResultsRangeDict

def getResultsRange(self):
    """Returns the valid result range for this routine analysis based on the
    results ranges defined in the Analysis Request this routine analysis is
    assigned to.

    A routine analysis will be considered out of range if it result falls
    out of the range defined in "min" and "max". If there are values set for
    "warn_min" and "warn_max", these are used to compute the shoulders in
    both ends of the range. Thus, an analysis can be out of range, but be
    within shoulders still.
    :return: A dictionary with keys "min", "max", "warn_min" and "warn_max"
    :rtype: dict
    """
    specs = ResultsRangeDict()
    analysis_request = self.getRequest()
    if not analysis_request:
        return specs

    keyword = self.getKeyword()
    ar_ranges = analysis_request.getResultsRange()
    # Get the result range that corresponds to this specific analysis
    an_range = [rr for rr in ar_ranges if rr.get('keyword', '') == keyword]
    rr = an_range and an_range[0].copy() or specs

    # Calculated Specification
    calc_uid = rr.get("calculation")
    calc = api.get_object_by_uid(calc_uid, None)
    if calc:
        spec = rr.copy()
        spec["analysis_uid"] = self.UID()
        calc_spec = calc.calculate_result(mapping={"spec": spec}, default=rr)
        if calc_spec:
            rr.update(calc_spec)

    return rr
