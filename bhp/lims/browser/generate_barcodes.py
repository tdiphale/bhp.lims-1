# -*- coding: utf-8 -*-

import os
import re
from collections import OrderedDict

from bhp.lims import bhpMessageFactory as _
from bhp.lims import logger
from bhp.lims.decorators import returns_super_model
from bika.lims import api
from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GenerateBarcodesView(BrowserView):
    """Generates barcodes from ARs
    """
    template = ViewPageTemplateFile("templates/generate_barcodes.pt")

    def __init__(self, context, request):
        super(GenerateBarcodesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.exit_url = self.context.absolute_url()

    def __call__(self):
        form = self.request.form
        form_submitted = form.get("submitted", False)
        form_print = form.get("print", False)
        form_abort = form.get("abort", False)
        objs = self.get_objects()

        if not objs:
            self.add_status_message(_("No items selected for printing"))
            referer = self.request.getHeader("referer")
            return self.request.response.redirect(referer)

        # Handle form submit
        if form_submitted and form_print:
            logger.info("*** PRINT ***")
            printer_uid = form.get("barcode_printer", "")
            printer = self.get_object_by_uid(printer_uid)
            filepath = printer.getPrinterPath()
            for obj in objs:
                # format the barcode template
                barcode = self.format_template_for(obj, printer.getTemplate())
                # format the filename template
                filename = self.format_template_for(obj, printer.getFileName())
                self.write(barcode, filename, filepath)

            message = _("Barcode printed for {}".format(
                ",".join(map(api.get_title, objs))))
            self.add_status_message(message, "info")
            return self.request.response.redirect(self.exit_url)

        # Handle form abort
        if form_submitted and form_abort:
            logger.info("*** ABORT ***")
            message = _("Barcode print aborted")
            self.add_status_message(message, "warn")
            return self.request.response.redirect(self.exit_url)

        # render the template
        return self.template()

    def parse_placeholders(self, template):
        """Parse ${...} placeholders to a list of keys
        """
        return re.findall("\$\{(.*?)\}", template)

    def format_template_for(self, obj, template, **kw):
        """Format the template for the given object
        """
        # convert the object into a SuperModel
        model = self.to_super_model(obj)
        # extract the placeholders from the template
        keys = self.parse_placeholders(template)

        # N.B. We can not use string.Template, because it is not capable to
        #      interpolate dotted keys, e.g. ${Client.ClientID}
        for key in keys:
            value = data.get(key)
            template = template.replace("${%s}" % key, value)

        # allow key override by keywords
        data.update(kw)

        return template

    def write(self, contents, filename, filepath):
        """Writes the contents to the given path
        """
        if not os.path.exists(filepath):
            return False
        with open(os.path.join(filepath, filename), "w") as f:
            f.write(contents)
        return True

    def get(self, obj, key):
        v = obj
        for k in key.split("."):
            if v is None:
                logger.warn("No reference found for key={} on object={}"
                            .format(key, obj.id))
                return "*** {} is not a valid key ***".format(key)
            v = v.get(k)
        if callable(v):
            v = v()
        return v

    def to_string(self, value):
        """Convert a vaue to a CSV compatible string
        """
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        if value is None:
            value = ""
        return str(value)

    def get_objects(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", [])
        # handle 'uids' GET parameter coming from a redirect
        if isinstance(uids, basestring):
            uids = uids.split("; ")
        unique_uids = OrderedDict().fromkeys(uids).keys()
        return map(self.get_object_by_uid, unique_uids)

    @returns_super_model
    def to_super_model(self, obj_or_objs):
        """Returns a SuperModel for a given object or a list of Supermodels if
        a list of objects was passed in
        """
        return obj_or_objs

    def get_printers(self):
        """Return all available barcode printers
        """
        query = {
            "portal_type": "BarcodePrinter",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "inactive_state": "active",
        }
        results = api.search(query, "bika_setup_catalog")
        return map(api.get_object, results)

    def get_base_info(self, obj):
        """Extract the base info from the given object
        """
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

    def get_printer_data(self):
        """Returns a list of printer data
        """
        for obj in self.get_printers():
            info = self.get_base_info(obj)
            yield info

    def get_ar_data(self):
        """Returns a list of AR data
        """
        for obj in self.get_objects():
            info = self.get_base_info(obj)
            yield info

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
