# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from bhp.lims import bhpMessageFactory as _
from bhp.lims.browser import add_column
from bhp.lims.config import GENDERS_ANY
from bika.lims.browser.client.views.analysisspecs import ClientAnalysisSpecsView
from bika.lims.controlpanel.bika_analysisspecs import AnalysisSpecsView


class AnalysisSpecsFolderContentsView(AnalysisSpecsView):

    def __init__(self, context, request):
        super(AnalysisSpecsFolderContentsView, self).__init__(context, request)
        add_column(self, "gender", {"title": _("Gender"), "sortable": False})
        add_column(self, "age", {"title": _("Age"), "sortable": False})

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        AnalysisSpecsView.folderitem(self, obj, item, index)
        return folder_item(self, obj, item, index)


class ClientAnalysisSpecsFolderContentsView(ClientAnalysisSpecsView):

    def __init__(self, context, request):
        super(ClientAnalysisSpecsFolderContentsView, self).__init__(context, request)
        add_column(self, "gender", {"title": _("Gender"), "sortable": False})
        add_column(self, "age", {"title": _("Age"), "sortable": False})

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        ClientAnalysisSpecsView.folderitem(self, obj, item, index)
        return folder_item(self, obj, item, index)


def folder_item(listing, obj, item, index):
    gender = obj.Schema().getField('Gender').get(obj)
    agefrom = obj.Schema().getField('Agefrom').get(obj)
    ageto = obj.Schema().getField('Ageto').get(obj)
    age = ""
    if agefrom and ageto:
        age = _('{} <= [Age] < {}').format(agefrom, ageto)
    elif agefrom:
        age = _('>= {}').format(agefrom)
    elif ageto:
        age = _('< {}').format(ageto)

    item["gender"] = GENDERS_ANY.getValue(gender, "")
    item['age'] = age
    return item