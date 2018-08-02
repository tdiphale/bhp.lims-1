# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims.browser.shipment import ShipmentListingDecorator
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from bika.lims.browser.client import ClientAnalysisRequestsView as ClientView


class AnalysisRequestsView(BaseView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        ShipmentListingDecorator().render(self)


class ClientAnalysisRequestsView(ClientView):

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        ShipmentListingDecorator().render(self)
