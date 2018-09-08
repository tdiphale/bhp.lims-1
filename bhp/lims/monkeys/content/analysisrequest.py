# -*- coding: utf-8 -*-


def getAncestors(self, all_ancestors=True):
    """Returns the ancestor(s) of this Analysis Request
    param all_ancestors: include all ancestors, not only the parent
    """
    parent = self.getParentAnalysisRequest()
    if not parent:
        return list()
    if not all_ancestors:
        return [parent]
    return [parent] + getAncestors(parent, all_ancestors=True)


def getDescendants(self, all_descendants=True):
    """Returns the descendant Analysis Requests
    :param all_descendants: include all descendants, not only the children
    """
    children = self.getBackReferences('AnalysisRequestParentAnalysisRequest')
    if not all_descendants:
        return children

    descendants = []
    for child in children:
        descendants.append(child)
        descendants += getDescendants(child)
    return descendants

