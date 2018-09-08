from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING


def searchResults(self, REQUEST=None, used=None, **kw):
    """Search the catalog

    Search terms can be passed in the REQUEST or as keyword
    arguments.

    The used argument is now deprecated and ignored
    """

    if REQUEST and REQUEST.get('getRequestUID') \
            and self.id == CATALOG_ANALYSIS_LISTING:

        request = REQUEST.copy()
        orig_uids = request.get('getRequestUID')
        if isinstance(orig_uids, list):
            results = list()
            for orig_uid in orig_uids:
                request['getRequestUID'] = [orig_uid]
                results += self.searchResults(REQUEST=request, used=used, **kw)
            return results

        # Get all the analyses, those from descendant ARs included
        del request['getRequestUID']
        request['getAncestorsUIDs'] = orig_uids

        logger.info("** Monkey ZCatalog.searchResults. getAncestorsUIDs: {} **"
                    .format(repr(orig_uids)))
        results = self.searchResults(REQUEST=request, used=used, **kw)

        # Get the primary analyses
        primary = filter(lambda an: an.getParentUID in orig_uids, results)
        wo_results = filter(lambda an: not an.getResult, primary)
        results = filter(lambda an: an not in wo_results, results)

        # Exclude those primary analyses w/o results, but with counterparts
        for analysis in results:
            keyword = analysis.getKeyword
            wo_results = filter(lambda an: an.getKeyword == keyword, wo_results)
            if not wo_results:
                break

        return results + wo_results

    # Normal search
    return self._catalog.searchResults(REQUEST, used, **kw)
