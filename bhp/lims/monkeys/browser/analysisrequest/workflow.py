
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from bika.lims import PMF, api
from bika.lims import bikaMessageFactory as _
from bika.lims.permissions import *
from bika.lims.utils import encode_header
from bika.lims.utils import t
from email.Utils import formataddr

def notify_ar_retract(self, ar, newar):
    bika_setup = api.get_bika_setup()
    laboratory = bika_setup.laboratory
    lab_address = "<br/>".join(laboratory.getPrintAddress())
    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = t(_("Erroneus result publication from ${request_id}",
                              mapping={"request_id": ar.getId()}))
    mime_msg['From'] = formataddr(
        (encode_header(laboratory.getName()),
         laboratory.getEmailAddress()))
    to = []
    contact = ar.getContact()
    if contact:
        to.append(formataddr((encode_header(contact.Title()),
                              contact.getEmailAddress())))
    for cc in ar.getCCContact():
        formatted = formataddr((encode_header(cc.Title()),
                                cc.getEmailAddress()))
        if formatted not in to:
            to.append(formatted)

    managers = self.context.portal_groups.getGroupMembers('LabManagers')
    for bcc in managers:
        user = self.portal.acl_users.getUser(bcc)
        if user:
            uemail = user.getProperty('email')
            ufull = user.getProperty('fullname')
            formatted = formataddr((encode_header(ufull), uemail))
            if formatted not in to:
                to.append(formatted)
    mime_msg['To'] = ','.join(to)
    aranchor = "<a href='%s'>%s</a>" % (ar.absolute_url(),
                                        ar.getId())
    naranchor = "<a href='%s'>%s</a>" % (newar.absolute_url(),
                                         newar.getId())
    addremarks = ('addremarks' in self.request and ar.getRemarks()) and ("<br/><br/>" + _("Additional remarks:") +
                                                                         "<br/>" + ar.getRemarks().split("===")[
                                                                             1].strip() +
                                                                         "<br/><br/>") or ''
    sub_d = dict(request_link=aranchor,
                 new_request_link=naranchor,
                 remarks=addremarks,
                 lab_address=lab_address)
    body = Template(
                    "Some non-conformities have been detected in the"
                    " results report published for Analysis Request $request_link."
                    " A new Analysis Request $new_request_link has been created automatically,"
                    " and the previous request has been invalidated.<br/>"
                    " The root cause is under investigation and corrective action has been initiated.<br/><br/>"
                    "$remarks $lab_address").safe_substitute(sub_d)
    msg_txt = MIMEText(safe_unicode(body).encode('utf-8'),
                       _subtype='html')
    mime_msg.preamble = 'This is a multi-part MIME message.'
    mime_msg.attach(msg_txt)
    try:
        host = getToolByName(self.context, 'MailHost')
        host.send(mime_msg.as_string(), immediate=True)
    except Exception as msg:
        message = _('Unable to send an email to alert lab '
                    'client contacts that the Analysis Request has been '
                    'retracted: ${error}',
                    mapping={'error': safe_unicode(msg)})
        self.context.plone_utils.addPortalMessage(message, 'warning')