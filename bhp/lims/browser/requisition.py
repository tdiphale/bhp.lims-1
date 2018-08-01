# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
import os
import tempfile
from base64 import b64encode
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from barcode.writer import ImageWriter
from barcode import Code39
from bhp.lims import logger
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.utils import createPdf


class RequisitionFormPdf(BrowserView):
    template = ViewPageTemplateFile("templates/requisition.pt")
    icon = None

    def __init__(self, context, request):

        super(RequisitionFormPdf, self).__init__(context, request)

        self.analysis_requests = []
        if ISample.providedBy(context):
            self.analysis_requests = context.getAnalysisRequests()
        elif IAnalysisRequest.providedBy(context):
            self.analysis_requests = [context]

    def __call__(self):
        return self.template()

    def get_barcode(self, instance):
        ean = Code39(u''+str(instance.id), writer=ImageWriter())
        barcode_img = tempfile.mktemp(suffix='.png')
        localFile = open(barcode_img, 'w')
        ean.write(localFile)
        localFile.close()
        img = open(barcode_img, 'r')
        img_str = img.read()
        return "data:image/png;base64,{}".format(b64encode(img_str))

    def get(self, instance, field_name):
        return instance.Schema().getField(field_name).get(instance)

    def get_contact_name(self):
        user = api.get_current_user()
        contact = api.get_user_contact(user)
        return contact.getFullname()

    def get_contact_phone(self):
        user = api.get_current_user()
        contact = api.get_user_contact(user)
        return contact.getBusinessPhone()

    def get_contact_title(self):
        user = api.get_current_user()
        contact = api.get_user_contact(user)
        return contact.getJobTitle()

    def getDepartment(self):
        user = api.get_current_user()
        contact = api.get_user_contact(user)
        return contact.getDepartment()






def generate_requisition_pdf(ar_or_sample):
    if not ar_or_sample:
        logger.warn("No Analysis Request or Sample provided")
        return
    if ISample.providedBy(ar_or_sample):
        for ar in ar_or_sample.getAnalysisRequests():
            generate_requisition_pdf(ar)
        return
    elif not IAnalysisRequest.providedBy(ar_or_sample):
        logger.warn("Type not supported: {}".format(repr(ar_or_sample)))
        return

    html = RequisitionFormPdf(ar_or_sample, ar_or_sample.REQUEST).template()
    html = safe_unicode(html).encode('utf-8')
    filename = '%s-requisition' % ar_or_sample.id
    pdf_fn = tempfile.mktemp(suffix=".pdf")
    pdf = createPdf(htmlreport=html, outfile=pdf_fn)
    if not pdf:
        logger.warn("Unable to generate the PDF of requisition form for {}".
                    format(ar_or_sample.id))
        return

    # Attach the pdf to the Analysis Request
    attid = ar_or_sample.aq_parent.generateUniqueId('Attachment')
    att = _createObjectByType(
        "Attachment", ar_or_sample.aq_parent, attid)
    att.setAttachmentFile(open(pdf_fn))
    # Awkward workaround to rename the file
    attf = att.getAttachmentFile()
    attf.filename = '%s.pdf' % filename
    att.setAttachmentFile(attf)
    att.unmarkCreationFlag()
    renameAfterCreation(att)
    atts = ar_or_sample.getAttachment() + [att] if \
        ar_or_sample.getAttachment() else [att]
    atts = [a.UID() for a in atts]
    ar_or_sample.setAttachment(atts)
    os.remove(pdf_fn)
