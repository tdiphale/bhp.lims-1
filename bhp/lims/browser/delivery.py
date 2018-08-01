# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
import os
import tempfile

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bhp.lims import logger
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.utils import createPdf


class DeliveryFormPdf(BrowserView):
    template = ViewPageTemplateFile("templates/delivery.pt")

    def __init__(self, context, request):
        super(DeliveryFormPdf, self).__init__(context, request)

        self.analysis_requests = []
        if ISample.providedBy(context):
            self.analysis_requests = context.getAnalysisRequests()
        elif IAnalysisRequest.providedBy(context):
            self.analysis_requests = [context]

    def __call__(self):
        return self.template()

    def get(self, instance, field_name):
        return instance.Schema().getField(field_name).get(instance)

    def get_contact_name(self):
        user = api.get_current_user()
        contact = api.get_user_contact(user)
        return contact.getFullname()

def generate_delivery_pdf(ar_or_sample):
    if not ar_or_sample:
        logger.warn("No Analysis Request or Sample provided")
        return

    if not ISample.providedBy(ar_or_sample) and \
            not IAnalysisRequest.providedBy(ar_or_sample):
        logger.warn("Type not supported: {}".format(repr(ar_or_sample)))
        return

    html = DeliveryFormPdf(ar_or_sample, ar_or_sample.REQUEST).template()
    html = safe_unicode(html).encode('utf-8')
    filename = '%s-delivery' % ar_or_sample.id
    pdf_fn = tempfile.mktemp(suffix=".pdf")
    pdf = createPdf(htmlreport=html, outfile=pdf_fn)
    if not pdf:
        logger.warn("Unable to generate the PDF of delivery form for {}".
                    format(ar_or_sample.id))
        return

    def _attach_to_ar(pdf, ar_brain_or_obj):
        ar = api.get_object(ar_brain_or_obj)
        attid = ar.aq_parent.generateUniqueId('Attachment')
        att = _createObjectByType(
            "Attachment", ar.aq_parent, attid)
        att.setAttachmentFile(open(pdf_fn))
        # Awkward workaround to rename the file
        attf = att.getAttachmentFile()
        attf.filename = '%s.pdf' % filename
        att.setAttachmentFile(attf)
        att.unmarkCreationFlag()
        renameAfterCreation(att)
        atts = ar.getAttachment() + [att] if ar.getAttachment() else [att]
        atts = [a.UID() for a in atts]
        ar.setAttachment(atts)

    # Attach the pdf to the Analysis Request
    if ISample.providedBy(ar_or_sample):
        for ar in ar_or_sample.getAnalysisRequests():
            _attach_to_ar(pdf, ar)
    elif IAnalysisRequest.providedBy(ar_or_sample):
        _attach_to_ar(pdf, ar_or_sample)

    os.remove(pdf_fn)
