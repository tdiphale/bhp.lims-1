# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

import collections

from Products.CMFCore.permissions import AddPortalContent
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import check_permission
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class CourierFolderContentsView(BikaListingView):
    """Listing view for all Couriers
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(CourierFolderContentsView, self).__init__(context, request)

        self.catalog = "portal_catalog"

        self.contentFilter = {
            "portal_type": "Courier",
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }

        self.context_actions = {}
        self.title = self.context.translate(_("Couriers"))
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bhp.images/courier_big.png")

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = collections.OrderedDict((
            ("getFullname", {
                "title": _("Full name"),
                "index": "sortable_title",
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"review_state": "active"},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns,
            }, {
                "id": "inactive",
                "title": _("Dormant"),
                "contentFilter": {"review_state": "inactive"},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns,
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns,
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

        # Render the Add button if the user has the Add permission
        if check_permission(AddPortalContent, self.context):
            self.context_actions[_("Add")] = {
                "url": "createObject?type_name=Courier",
                "icon": "++resource++bika.lims.images/add.png"
            }

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        fullname = obj.getFullname()
        url = obj.absolute_url()

        item["replace"]["getFullname"] = get_link(url, value=fullname)

        return item
