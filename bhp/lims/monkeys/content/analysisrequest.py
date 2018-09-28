# -*- coding: utf-8 -*-
from bhp.lims import api
from bika.lims.api.analysis import is_out_of_range

def getAncestors(self, all_ancestors=True):
    """Returns the ancestor(s) of this Analysis Request
    param all_ancestors: include all ancestors, not only the parent
    """
    parent = self.getPrimaryAnalysisRequest()
    if not parent:
        return list()
    if not all_ancestors:
        return [parent]
    return [parent] + parent.getAncestors(all_ancestors=True)


def getDescendants(self, all_descendants=True):
    """Returns the descendant Analysis Requests
    :param all_descendants: include all descendants, not only the children
    """
    children = self.getBackReferences('AnalysisRequestPrimaryAnalysisRequest')
    if not all_descendants:
        return children

    descendants = []
    for child in children:
        descendants.append(child)
        descendants += child.getDescendants()
    return descendants


def getPrimarySample(self):
    return api.get_field_value(self, "PrimarySample", None)


def getPrimaryAnalysisRequest(self):
    return api.get_field_value(self, "PrimaryAnalysisRequest", None)


def has_analyses_in_panic(self):
    analyses = self.getAnalyses(full_objects=True, retracted=False)
    for analysis in analyses:
        if is_out_of_range(analysis)[1]:
            return True
    return False
