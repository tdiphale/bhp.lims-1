# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims import api as _api
from bhp.lims import bhpMessageFactory as _
from bhp.lims.browser import add_column
from bhp.lims.browser.shipment import ShipmentListingDecorator
from bika.lims import api
from bika.lims.browser.client import ClientSamplesView as ClientView
from bika.lims.browser.sample import SamplesView as BaseView
from bika.lims.utils import get_link


class SamplesView(BaseView):

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        ShipmentListingDecorator().render(self)


class ClientSamplesView(ClientView):

    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        init_listing(self)

    def __call__(self):
        self.client_contact = api.get_user_contact(api.get_current_user(),
                                                   contact_types=['Contact'])
        return ClientView.__call__(self)

    def folderitem(self, obj, item, index):
        item = ClientView.folderitem(self, obj, item, index)
        return folder_listing_item(self, obj, item, index)

    def isItemAllowed(self, obj):
        """Only display the Analysis Requests that are not for internal use
        """
        if not ClientView.isItemAllowed(self, obj):
            return False

        # TODO Performance - This function wakes up the whole object
        # If the current user is a client contact, display non-internal Samples
        if self.client_contact:
            return not _api.get_field_value(obj, "InternalUse", False)
        return True


def init_listing(listing):
    primary = {"title": _("Primary Sample"),"sortable": True, "toggle": True}
    add_column(listing, 'primary', primary, after='getSampleID')
    ShipmentListingDecorator().render(listing)


def folder_listing_item(listing, obj, item, index):
    sample = api.get_object(obj)
    primary = _api.get_field_value(sample, 'PrimarySample', None)
    item["primary"] = ""
    if not primary:
        return item
    primary = api.get_object(primary)
    primary_id = primary.getSampleID()
    primary_url = primary.absolute_url()
    item["primary"] = primary.getSampleID()
    item["replace"]["primary"] = get_link(primary_url, value=primary_id)
    return item