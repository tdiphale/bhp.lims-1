# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from bika.lims import bikaMessageFactory as _
from bika.lims import api
from bika.lims.api.analysis import is_out_of_range
from bika.lims.utils import get_image

def _folder_item_specifications(self, analysis_brain, item):
    """Set the results range to the item passed in"""
    # Everyone can see valid-ranges
    item['Specification'] = ''
    analysis = api.get_object(analysis_brain)
    results_range = analysis.getResultsRange()
    if not results_range:
        return
    min_str = results_range.get('min', '')
    max_str = results_range.get('max', '')
    min_str = api.is_floatable(min_str) and "{0}".format(min_str) or ""
    max_str = api.is_floatable(max_str) and "{0}".format(max_str) or ""
    # Join with semi-colon to avoid confusion with commas as decimal mark
    specs = "; ".join([val for val in [min_str, max_str] if val])
    if not specs:
        return
    item["Specification"] = "[{}]".format(specs)

    # Show an icon if out of range
    out_range, out_shoulders = is_out_of_range(analysis_brain)
    if not out_range:
        return
    # At least is out of range
    img = get_image("exclamation.png", title=_("Result out of range"))
    if not out_shoulders:
        img = get_image("warning.png", title=_("Result in shoulder range"))
    self._append_html_element(item, "Result", img)
