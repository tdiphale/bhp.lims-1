# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims.browser.shipment import ShipmentListingDecorator
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
