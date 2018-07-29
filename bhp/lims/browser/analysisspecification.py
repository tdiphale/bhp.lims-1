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
        keyword = service.getKeyword()
        if keyword in self.specsresults:
            nitem["minpanic"] = self.specsresults[keyword].get("minpanic", "")
            nitem["maxpanic"] = self.specsresults[keyword].get("maxpanic", "")
        nitem["allow_edit"].extend(["minpanic", "maxpanic"])
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
