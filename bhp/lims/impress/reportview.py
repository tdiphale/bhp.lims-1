# -*- coding: utf-8 -*-

from bhp.lims import api as _api
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

    def get_age_str(self, model):
        years, months, days = _api.get_age(model.DateOfBirth, model.DateSampled)
        years = years and "{}y".format(years) or None
        months = months and "{}m".format(months) or None
        days = days and "{}d".format(days) or None
        age = filter(lambda val: val != None, [years, months, days])
        return " ".join(age)

    def get_analyses_by(self, model_or_collection,
                        title=None, poc=None, category=None,
                        hidden=False, retracted=False):
        """Returns a sorted list of Analyses for the given POC which are in the
        given Category
        """
        analyses = self.get_analyses(model_or_collection)
        if title is not None:
            analyses = filter(lambda an: an.Title() == title, analyses)
        if poc is not None:
            analyses = filter(lambda an: an.PointOfCapture == poc, analyses)
        if category is not None:
            analyses = filter(lambda an: an.Category == category, analyses)
        if not hidden:
            analyses = filter(lambda an: not an.Hidden, analyses)
        return self.sort_items(analyses)


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
