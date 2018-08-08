# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

import collections

from bhp.lims import bhpMessageFactory as _
from bika.lims import api
from bika.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationView as BaseView


class AnalysisSpecificationView(BaseView):

    def __init__(self, context, request, fieldvalue=[], allow_edit=True):
        BaseView.__init__(self, context, request, fieldvalue=fieldvalue,
                          allow_edit=allow_edit)

        # Add "min panic" and "max panic" fields.
        min_panic = {"title": _("Min panic"), "sortable": False}
        self.add_column('minpanic', min_panic, before='warn_min')

        max_panic = {"title": _("Max panic"), "sortable": False}
        self.add_column('maxpanic', max_panic, after='warn_max')

        calculation = {"title": _("Specification Calculation"),
                       "sortable": False, "type": "choices"}
        self.add_column("calculation", calculation, after='hidemax')

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        nitem = BaseView.folderitem(self, obj, item, index)
        service = api.get_object(obj)

        nitem["minpanic"] = ""
        nitem["maxpanic"] = ""
        nitem["calculation"] = ""
        keyword = service.getKeyword()
        if keyword in self.specsresults:
            specsresults = self.specsresults[keyword]
            nitem["minpanic"] = specsresults.get("minpanic", "")
            nitem["maxpanic"] = specsresults.get("maxpanic", "")
            nitem["calculation"] = specsresults.get("calculation", "")
        nitem["choices"]["calculation"] = self.get_calculations_choices()
        nitem["allow_edit"].extend(["minpanic", "maxpanic", "calculation"])
        return nitem

    def add_column(self, keyword, column, before=None, after=None):
        """ Adds a column in self.columns and self.review_states as well
        """
        if not before and not after:
            after = self.columns.keys()[-1]
        elif before and after:
            after = None

        new_columns = collections.OrderedDict()
        for key, value in self.columns.items():
            if before and before == key:
                new_columns[keyword] = column
            new_columns[key] = value
            if after and after == key:
                new_columns[keyword] = column
        if keyword not in new_columns:
            new_columns[keyword] = column
        self.columns = new_columns
        self.review_states[0]['columns'] = self.columns.keys()

    def get_calculations(self):
        """Returns the calculations
        """
        query = {
            "portal_type": "Calculation",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        return api.search(query, catalog="bika_setup_catalog")

    def get_calculations_choices(self):
        """Build a list of listing specific calculation choices
        """
        calculations = self.get_calculations()
        return map(
            lambda brain: {
                "ResultValue": api.get_uid(brain),
                "ResultText": api.get_title(brain)},
            calculations)
