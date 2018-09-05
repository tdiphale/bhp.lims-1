# -*- coding: utf-8 -*-

from bhp.lims import logger
from senaite.impress.analysisrequest.reportview import MultiReportView
from senaite.impress.analysisrequest.reportview import SingleReportView
from bika.lims.workflow import getTransitionDate


class BhpSingleReportView(SingleReportView):
    """BHP specific controller view for single-reports
    """

    def __init__(self, model, request):
        logger.info("BhpSingleReportView::__init__:model={}"
                    .format(model))
        super(BhpSingleReportView, self).__init__(model, request)


class BhpMultiReportView(MultiReportView):
    """BHP specific controller view for multi-reports
    """

    def __init__(self, collection, request):
        logger.info("BhpMultiReportView::__init__:collection={}"
                    .format(collection))
        super(BhpMultiReportView, self).__init__(collection, request)

    def get_transition_date(self, obj, transition=None):
        """Returns the date of the given Transition
        """
        if transition is None:
            return None
        return getTransitionDate(obj, transition, return_as_datetime=True)
