# -*- coding: utf-8 -*-

import collections

from bhp.lims import bhpMessageFactory as _
from bhp.lims.config import PRODUCT_NAME
from bhp.lims.interfaces import IBarcodePrinters
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


class BarcodePrinterListing(BikaListingView):
    """Listing of all available Barcode Printers
    """

    def __init__(self, context, request):
        super(BarcodePrinterListing, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "BarcodePrinter",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=BarcodePrinter",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Barcode Printers"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bhp.lims.static/images/barcodeprinters_big.png"
        )
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True}),
            ("PrinterPath", {
                "title": _("Printer Path"),
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"inactive_state": "active"},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Dormant"),
                "contentFilter": {"inactive_state": "inactive"},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()
        printerpath = obj.getPrinterPath()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description
        item["PrinterPath"] = printerpath

        return item


schema = ATFolderSchema.copy()


class BarcodePrinters(ATFolder):
    implements(IBarcodePrinters)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(BarcodePrinters, PRODUCT_NAME)
