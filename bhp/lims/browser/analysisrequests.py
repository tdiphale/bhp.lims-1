# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims import api as _api
from bhp.lims import bhpMessageFactory as _
from bhp.lims.browser import add_column
from bhp.lims.browser.shipment import ShipmentListingDecorator
from bika.lims import api
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from bika.lims.browser.client import ClientAnalysisRequestsView as ClientView
from bika.lims.utils import get_link

class AnalysisRequestsView(BaseView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        init_listing(self)

        partition_magic = {
            "id": "partition_magic",
            "title": _("Partition"),
            "url": "partition_magic"
        }

        for rs in self.review_states:
            if rs.get("custom_transitions") is None:
                rs["custom_transitions"] = []
            transitions = rs["custom_transitions"]
            transitions.append(partition_magic)
            rs["custom_transitions"] = transitions

    def folderitem(self, obj, item, index):
        item = BaseView.folderitem(self, obj, item, index)
        return folder_listing_item(self, obj, item, index)

class ClientAnalysisRequestsView(ClientView):

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        init_listing(self)

    def __call__(self):
        self.client_contact = api.get_user_contact(api.get_current_user(),
                                                   contact_types=['Contact'])
        return ClientView.__call__(self)

    def isItemAllowed(self, obj):
        """Only display the Analysis Requests that are not for internal use
        """
        if not ClientView.isItemAllowed(self, obj):
            return False

        # TODO Performance - This function wakes up the whole object
        # If the current user is a client contact, display non-internal ARs
        if self.client_contact:
            return not _api.get_field_value(obj, "InternalUse", False)
        return True

    def folderitem(self, obj, item, index):
        item = ClientView.folderitem(self, obj, item, index)
        return folder_listing_item(self, obj, item, index)


def init_listing(listing):
    primary = {"title": _("Primary Sample"), "sortable": True, "toggle": True}
    add_column(listing, 'primary', primary, before='getSample')
    ShipmentListingDecorator().render(listing)


def folder_listing_item(listing, obj, item, index):
    ar = api.get_object(obj)
    primary = _api.get_field_value(ar, 'PrimarySample', None) or ar.getSample()
    primary = api.get_object(primary)
    primary_id = primary.getSampleID()
    primary_url = primary.absolute_url()
    item["primary"] = primary.getSampleID()
    item["replace"]["primary"] = get_link(primary_url, value=primary_id)
    return item
