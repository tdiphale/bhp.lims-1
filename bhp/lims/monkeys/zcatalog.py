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
        orig_uid = request.get('getRequestUID')
        if isinstance(orig_uid, list):
            results = list()
            for uid in orig_uid:
                request['getRequestUID'] = [uid]
                results += self.searchResults(REQUEST=request, used=used, **kw)
            return results

        # Get all the analyses, those from descendant ARs included
        del request['getRequestUID']
        request['getAncestorsUIDs'] = orig_uid
        results = self.searchResults(REQUEST=request, used=used, **kw)
        primary = filter(lambda an: an.getParentUID == orig_uid, results)
        derived = filter(lambda an: an.getParentUID != orig_uid, results)
        derived_keys = map(lambda an: an.getKeyword, derived)
        results = filter(lambda an: an.getKeyword not in derived_keys, primary)
        return results + derived

    # Normal search
    return self._catalog.searchResults(REQUEST, used, **kw)
