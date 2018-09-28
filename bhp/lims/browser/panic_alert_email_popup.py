import plone.protect
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bhp.lims import bhpMessageFactory as _
from bika.lims import api
from bika.lims.api.analysis import is_out_of_range
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysisRequest
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class EmailPopupView(BrowserView):
    implements(IViewView)

    template = ViewPageTemplateFile("templates/panic_alert_email_popup.pt")

    def __init__(self, context, request):
        super(EmailPopupView, self).__init__(context, request)
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/warning_big.png"
        )
        self.recipients = []
        self.ccs = ''
        self.subject = ''
        self.body = ''

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        ar = api.get_object_by_uid(self.request.get('uid', None), None) or \
             self.context
        if not ar or not IAnalysisRequest.providedBy(ar):
            return self.template()

        # Set the default recipients for the email
        self.recipients = self.get_recipients(ar)
        # Set the subject
        self.subject = self.context.translate(
            _("Some results from ${ar} exceeded panic range",
              mapping={"ar": ar.getId()})
        )
        # Set the body of the message
        self.body = self.get_body_message(ar)

        return self.template()

    def getFormattedRecipients(self):
        outrecip = list()
        for recipient in self.recipients:
            name = recipient['name']
            email = recipient['email']
            outrecip.append("%s <%s>" % (name, email))
        return ', '.join(outrecip)

    def get_recipient(self, contact):
        if not contact:
            return None
        contact_obj = api.get_object(contact)
        email = contact_obj.getEmailAddress()
        if not email:
            return None
        return {'uid': api.get_uid(contact_obj),
                'name': contact_obj.Title(),
                'email': email}

    def get_recipients(self, ar):
        contacts = [ar.getContact(), ar.getCCContact()]
        recipients = map(lambda con: self.get_recipient(con), contacts)
        client = ar.getClient()
        client_email = client.getEmailAddress()
        if client_email:
            recipients.append({
                'uid': api.get_uid(client),
                'name': client.Title(),
                'email': client_email})
        return filter(lambda recipient: recipient, recipients)

    def get_panic_analyses_list_message(self, ar):
        translate = self.context.translate
        analyses = ar.getAnalyses(full_objects=True, retracted=False)
        messages = list()
        for analysis in analyses:
            if not is_out_of_range(analysis)[1]:
                continue
            messages.append(
                "- {0}, {1}: {2} {3}".format(analysis.Title(),
                                             translate(_("Result")),
                                             analysis.getFormattedResult(),
                                             analysis.getUnit()).strip()
            )
        return "\n".join(messages)

    def get_body_message(self, ar):
        laboratory = self.context.bika_setup.laboratory
        lab_address = "\n".join(laboratory.getPrintAddress())
        return self.context.translate(
            _("Some results from the Analysis Request ${ar} "
              "exceeded the panic levels that may indicate an "
              "imminent life-threatening condition: \n\n${arlist}\n"
              "\n\n${lab_address}",
              mapping={'ar': ar.getId(),
                       'arlist': self.get_panic_analyses_list_message(ar),
                       'lab_address': lab_address})
        )
