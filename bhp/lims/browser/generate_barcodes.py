# -*- coding: utf-8 -*-

import os
import re
import subprocess
import os
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
                self.send_to_printer(printer.Title(), filename, filepath)

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

    def format_template_for(self, obj, template, default="", **kw):
        """Format the template for the given object
        """
        # convert the object into a SuperModel
        model = self.to_super_model(obj)
        # extract the placeholders from the template
        keys = self.parse_placeholders(template)

        # N.B. We can not use string.Template, because it is not capable to
        #      interpolate dotted keys, e.g. ${DateSampled|to_date}
        for key in keys:
            value = default
            # Split the value into Key|Converter
            splitted = key.split("|")
            if len(splitted) == 2:
                # the key is the first part
                k = splitted[0]
                value = kw.get(k) or model.get(k)
                converter = getattr(self, splitted[1], None)
                if callable(converter):
                    value = converter(value)
            else:
                value = kw.get(key) or self.get(model, key)

            # Always ensure a string value
            value = self.to_string(value)
            template = template.replace("${%s}" % key, value)

        return template

    def send_to_printer(self, printer_name, file_name, file_path):
        """Send the file to the printer
        """
        path = os.path.join(file_path, file_name)
        command = ["lpr", "-P", printer_name, "-o", "raw", path]
        subprocess.call(command)

    def write(self, contents, filename, filepath):
        """Writes the contents to the given path
        """
        if not os.path.exists(filepath):
            return False
        with open(os.path.join(filepath, filename), "w") as f:
            f.write(contents)
        return True

    def get(self, obj, key):
        if not obj or not key:
            return ""
        parts = key.split(".")
        if len(parts) == 1:
            v = obj.get(key)
            if v is None:
                logger.warn("No reference found for key={} on object={}"
                            .format(key, obj.id))
                return "*** {} is not a valid key ***".format(key)
            if callable(v):
                v = v()
            return v
        nkey = '.'.join(parts[1:])
        nobj = obj.get(parts[0])
        return self.get(nobj, nkey)

    def to_string(self, value):
        """Convert a value to a string
        """
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        if value is None:
            value = ""
        return str(value)

    def to_date(self, value, fmt="%d/%m/%Y"):
        """Convert a value to a datestring
        """
        if isinstance(value, DateTime):
            return value.strftime(fmt)
        return value

    def to_long_date(self, value, fmt="%d/%m/%Y %H:%M"):
        """Convert a value to a datestring
        """
        return self.to_date(value, fmt=fmt)

    def get_objects(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", [])
        if not uids:
            uids = self.request.form.get("items", [])
            uids = uids.split(',')
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
