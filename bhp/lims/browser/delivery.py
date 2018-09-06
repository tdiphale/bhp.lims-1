# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
import tempfile

from base64 import b64encode

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from barcode import Code39
from barcode.writer import ImageWriter
from bhp.lims import logger
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.utils import createPdf


class DeliveryFormPdf(BrowserView):
    template = ViewPageTemplateFile("templates/delivery.pt")

    def __init__(self, context, request, analysis_requests=None):
        super(DeliveryFormPdf, self).__init__(context, request)

        self.analysis_requests = analysis_requests
        if not self.analysis_requests:
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

    def get_barcode(self, instance):
        ean = Code39(u''+str(instance.id), writer=ImageWriter())
        ean.default_writer_options.update(font_size=20)
        barcode_img = tempfile.mktemp(suffix='.png')
        localFile = open(barcode_img, 'w')
        ean.write(localFile)
        localFile.close()
        img = open(barcode_img, 'r')
        img_str = img.read()
        return "data:image/png;base64,{}".format(b64encode(img_str))


def generate_delivery_pdf(context, ars_or_samples):
    if not ars_or_samples:
        logger.warn("No Analysis Requests or Samples provided")
        return

    if ISample.providedBy(ars_or_samples) or \
        IAnalysisRequest.providedBy(ars_or_samples):
        return generate_delivery_pdf([ars_or_samples])

    if not isinstance(ars_or_samples, list):
        logger.warn("Type not supported: {}".format(repr(ars_or_samples)))
        return

    html = DeliveryFormPdf(context, context.REQUEST,
                           analysis_requests=ars_or_samples).template()
    html = safe_unicode(html).encode("utf-8")
    filename = "delivery"
    pdf_fn = tempfile.mktemp(suffix=".pdf")
    pdf = createPdf(htmlreport=html, outfile=pdf_fn)
    if not pdf:
        ar_ids = map(lambda ar: ar.id, ars_or_samples)
        logger.warn("Unable to generate the PDF of delivery form for {}".
                    format(' '.join(ar_ids)))
        return None

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

    for ar_or_sample in ars_or_samples:
        # Attach the pdf to the Analysis Request
        if ISample.providedBy(ar_or_sample):
            for ar in ar_or_sample.getAnalysisRequests():
                _attach_to_ar(pdf, ar)
        elif IAnalysisRequest.providedBy(ar_or_sample):
            _attach_to_ar(pdf, ar_or_sample)

    return pdf_fn
