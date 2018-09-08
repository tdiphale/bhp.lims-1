from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.permissions import ViewRetractedAnalyses


def get(self, instance, **kwargs):
    """Returns a list of Analyses assigned to this AR

    Return a list of catalog brains unless `full_objects=True` is passed.
    Overrides "ViewRetractedAnalyses" when `retracted=True` is passed.
    Other keyword arguments are passed to bika_analysis_catalog

    :param instance: Analysis Request object
    :param kwargs: Keyword arguments to be passed to control the output
    :returns: A list of Analysis Objects/Catalog Brains
    """
    full_objects = kwargs and kwargs.get("full_objects", False)
    reflexed = kwargs and kwargs.get("get_reflexed", True)
    retracted = kwargs and kwargs.get("retracted", True)
    if retracted:
        mtool = getToolByName(instance, 'portal_membership')
        retracted = mtool.checkPermission(ViewRetractedAnalyses, instance)

    catalog = getToolByName(instance, CATALOG_ANALYSIS_LISTING)
    query =  dict([(k, v) for k, v in kwargs.items() if k in catalog.indexes()])
    query['portal_type'] = "Analysis"
    query['getRequestUID'] = api.get_uid(instance)
    analyses = catalog(query)
    if not full_objects and reflexed and retracted:
        return analyses

    out_analyses = list()
    for analysis in analyses:
        analysis_obj = None
        if not retracted and analysis.review_state == 'retracted':
            continue
        if not reflexed:
            analysis_obj = api.get_object(analysis)
            if analysis_obj.getReflexRuleActionsTriggered():
                continue
        if full_objects:
            analysis = analysis_obj and analysis_obj or api.get_object(analysis)
        out_analyses.append(analysis)
    return out_analyses
