# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from bika.lims import bikaMessageFactory as _
from bika.lims import api
from bika.lims.api.analysis import is_out_of_range, get_formatted_interval
from bika.lims.utils import get_image

def _folder_item_specifications(self, analysis_brain, item):
    """Set the results range to the item passed in"""
    # Everyone can see valid-ranges
    item['Specification'] = ''
    analysis = api.get_object(analysis_brain)
    results_range = analysis.getResultsRange()
    if not results_range:
        return

    # Display the specification interval
    item["Specification"] = get_formatted_interval(results_range, "")

    # Show an icon if out of range
    out_range, out_shoulders = is_out_of_range(analysis_brain)
    if not out_range:
        return
    # At least is out of range
    img = get_image("exclamation.png", title=_("Result out of range"))
    if not out_shoulders:
        img = get_image("warning.png", title=_("Result in shoulder range"))
    self._append_html_element(item, "Result", img)
