# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims import api as _api
from bhp.lims.browser.shipment import ShipmentListingDecorator
from bika.lims import api
from bika.lims.browser.client import ClientSamplesView as ClientView
from bika.lims.browser.sample import SamplesView as BaseView


class SamplesView(BaseView):

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        ShipmentListingDecorator().render(self)


class ClientSamplesView(ClientView):

    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        ShipmentListingDecorator().render(self)

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
        # If the current user is a client contact, display non-internal Samples
        if self.client_contact:
            return not _api.get_field_value(obj, "InternalUse", False)
        return True