# -*- coding: utf-8 -*-

import collections
from StringIO import StringIO

from bhp.lims import logger
from bika.lims import api
from DateTime import DateTime
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from plone.memoize.ram import cache
from Products.CMFPlone.CatalogTool import sortable_title
from Products.Five.browser import BrowserView
from senaite.core.supermodel import SuperModel
from Products.ATContentTypes.utils import DT2dt


REVIEW_STATE_MAP = {
}


def get_cache_key(method, instance, obj, key):
    cachekey = (obj.uid, key)
    return cachekey


def to_string(obj, key, value):
    """Convert a vaue to a CSV compatible string
    """
    if isinstance(value, unicode):
        value = value.encode("utf-8")
    if value is None:
        value = ""
    return value


def to_date(obj, key, value, fmt="%d/%m/%y"):
    if not isinstance(value, DateTime):
        return ""
    return DT2dt(value).strftime(fmt)


def to_long_date(obj, key, value, fmt="%d/%m/%y %H:%M"):
    return to_date(obj, key, value, fmt=fmt)


def length(obj, key, value):
    if not isinstance(value, collections.Iterable):
        return 0
    return len(value)


def to_wf_state(obj, key, value):
    if not isinstance(value, basestring):
        return value
    return REVIEW_STATE_MAP.get(value, value)


ROWS = [
    # TITLE, ATTRIBUTE, CONVERTER FUNCTION
    (u"Request-ID", "getId", to_string),
    (u"Client-ID", "Client.ClientID", to_string),
    (u"Client Name", "getClientTitle", to_string),
    (u"Contact", "getContactFullName", to_string),
    (u"Sample Type", "getSampleTypeTitle", to_string),
    (u"Sample Condition", "SampleCondition.title", to_string),
    (u"Client Reference", "ClientReference", to_string),
    (u"Sample Point", "getSamplePointTitle", to_string),
    (u"Analyse", "Analysis.Title", to_string),
    (u"Unit", "Analysis.Unit", to_string),
    # (u"Sort Key", "Analysis.SortKey", to_string),
    (u"Analyst", "Analysis.getAnalystName", to_string),
    (u"Date Created", "Analysis.created", to_long_date),
    (u"Date Sampled", "getDateSampled", to_long_date),
    (u"Date Received", "getDateReceived", to_long_date),
    (u"Date Captured", "Analysis.getResultCaptureDate", to_long_date),
    (u"Date Verified", "Analysis.getDateVerified", to_long_date),
    (u"Date Published", "getDatePublished", to_long_date),
    (u"Status", "Analysis.review_state", to_wf_state),
    (u"Price", "getSubtotalTotalPrice", to_string),
]


class ExportView(BrowserView):
    """Data Export View
    """

    def __init__(self, context, request):
        super(ExportView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # return CSV
        if self.request.get("csv", False):
            return self.get_csv()

        # Excel download
        now = DateTime().strftime("%d.%m.%Y")
        name = u"LIMS-Export-{}".format(now)
        filename = u"{}.xlsx".format(name)
        return self.download(self.get_excel(), filename)

    @property
    def header(self):
        return map(lambda item: item[0], ROWS)

    def get_csv(self):
        output = StringIO()
        lines = self.get_data()
        lines.insert(0, self.header)
        for line in lines:
            output.write(",".join(map(self.safe_unicode, line)) + "\n")
        return output.getvalue()

    def get_excel(self):
        """Export data as Excel
        """
        now = DateTime().strftime("%d.%m.%Y")
        workbook = Workbook()
        sheet = workbook.get_active_sheet()
        sheet.append(self.header)
        sheet.title = "LIMS Export {}".format(now)
        for row in self.get_data():
            sheet.append(row)
        return save_virtual_workbook(workbook)

    def download(self, data, filename, type="text/csv"):
        response = self.request.response
        response.setHeader("Content-Disposition",
                           "attachment; filename={}".format(
                               filename.encode("utf8")))
        response.setHeader("Content-Type", "{}; charset=utf-8".format(type))
        response.setHeader("Content-Length", len(data))
        response.setHeader("Cache-Control", "no-store")
        response.setHeader("Pragma", "no-cache")
        response.write(data)

    def get_sortable_title(self, analysis):
        analysis = api.get_object(analysis)
        sort_key = analysis.getSortKey()
        if sort_key is None:
            sort_key = 999999
        title = sortable_title(analysis)
        if callable(title):
            title = title()
        return "{:010.3f}{}".format(sort_key, title)

    def get_analyses(self, ar):
        analyses = ar.getAnalyses()
        sorted_analyses = sorted(analyses, key=self.get_sortable_title)
        return sorted_analyses

    def search(self):
        """Search all ARs of the system
        """
        catalog = api.get_tool("bika_catalog_analysisrequest_listing")

        query = {
            "portal_type": "AnalysisRequest",
            "sort_on": "created",
            "sort_order": "descending",
            "inactive_state": "active",
        }

        # review_state
        review_state = self.request.get("review_state")
        if review_state in REVIEW_STATE_MAP:
            query["review_state"] = review_state

        # limit
        limit = self.request.get("limit", "30")
        if limit.isdigit():
            limit = int(limit)
            if limit > 0:
                query["sort_limit"] = int(limit)

        return catalog(query)

    def get_data(self):
        rows = []

        ars = self.search()
        total = len(ars)
        logger.info("Exporting data of {} ARs".format(total))

        for num, ar in enumerate(ars):
            ar = SuperModel(api.get_uid(ar))

            for an in self.get_analyses(ar):
                data = []
                an = SuperModel(api.get_uid(an))
                for row in ROWS:
                    model = ar
                    title, key, converter = row
                    if key.startswith("Analysis"):
                        key = ".".join(key.split(".")[1:])
                        model = an
                    value = self.get(model, key)
                    data.append(converter(model, key, value))
                rows.append(data)

            if num % 100 == 0:
                logger.info("Exported {}/{}".format(num, total))

        return rows

    @cache(get_cache_key)
    def get(self, obj, key):
        """Extract the value from the object
        """
        v = obj
        for k in key.split("."):
            if v is None:
                # logger.warn("No reference found for key={} on object={}"
                #             .format(key, obj.id))
                break
            v = v.get(k)
        if key in obj.brain:
            return obj.brain[key]
        if callable(v):
            v = v()
        return v

    def safe_unicode(self, value, encoding="utf-8"):
        """Convert the value into a unicode
        """
        if not isinstance(value, basestring):
            return unicode(value)
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            try:
                value = unicode(value, encoding)
            except (UnicodeDecodeError):
                value = value.decode("utf-8", "replace")
        return value
