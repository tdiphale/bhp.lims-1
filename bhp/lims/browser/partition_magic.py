# -*- coding: utf-8 -*-

from collections import OrderedDict

from bhp.lims import logger
from bhp.lims.decorators import returns_super_model
from bika.lims import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

DEFAULT_NUMBER_OF_PARTITIONS = 0


class PartitionMagicView(BrowserView):
    """Manage Partitions of primary ARs
    """
    template = ViewPageTemplateFile("templates/partition_magic.pt")

    def __init__(self, context, request):
        super(PartitionMagicView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)

        # Buttons
        form_preview = form.get("button_preview", False)
        form_create = form.get("create", False)
        form_cancel = form.get("cancel", False)

        # objs = self.get_objects()

        # # No ARs selected
        # if not objs:
        #     return self.redirect(message=_("No items selected"),
        #                          level="warning")

        return self.template()

    def get_ar_data(self):
        """Returns a list of AR data
        """
        for obj in self.get_objects():
            info = self.get_base_info(obj)
            info.update({
                "analyses": self.get_analysis_data_for(obj),
                "sampletype": self.get_base_info(obj.getSampleType()),
                "number_of_partitions": self.get_number_of_partitions_for(obj),
            })
            yield info

    def get_sampletype_data(self):
        """Returns a list of SampleType data
        """
        for obj in self.get_sampletypes():
            info = self.get_base_info(obj)
            yield info

    def get_objects(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", "")
        if not uids:
            # check for the `items` parammeter
            uids = self.request.form.get("items", "")
        if isinstance(uids, basestring):
            uids = uids.split(",")
        unique_uids = OrderedDict().fromkeys(uids).keys()
        return filter(None, map(self.get_object_by_uid, unique_uids))

    def get_sampletypes(self):
        """Returns the available SampleTypes of the system
        """
        query = {
            "portal_type": "SampleType",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "inactive_state": "active",
        }
        results = api.search(query, "bika_setup_catalog")
        return map(api.get_object, results)

    @returns_super_model
    def to_super_model(self, obj_or_objs):
        """Returns a SuperModel for a given object or a list of Supermodels if
        a list of objects was passed in
        """
        return obj_or_objs

    def get_analysis_data_for(self, ar):
        """Return the Analysis data for this ar
        """
        analyses = ar.getAnalyses()
        out = []
        for an in analyses:
            out.append(self.get_base_info(an))
        return out

    def get_number_of_partitions_for(self, ar):
        """Return the number of selected partitions
        """
        uid = api.get_uid(ar)
        num = self.request.get("primary", {}).get(uid, DEFAULT_NUMBER_OF_PARTITIONS)
        try:
            num = int(num)
        except (TypeError, ValueError):
            num = DEFAULT_NUMBER_OF_PARTITIONS
        if num < 0:
            return 0
        return num

    def get_base_info(self, obj):
        """Extract the base info from the given object
        """
        obj = api.get_object(obj)
        review_state = api.get_workflow_status_of(obj)
        state_title = review_state.capitalize().replace("_", " ")
        return {
            "obj": obj,
            "id": api.get_id(obj),
            "uid": api.get_uid(obj),
            "title": api.get_title(obj),
            "path": api.get_path(obj),
            "url": api.get_url(obj),
            "review_state": review_state,
            "state_title": state_title,
        }

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
