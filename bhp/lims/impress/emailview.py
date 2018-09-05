from senaite.impress.emailview import EmailView as BaseEmailView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class EmailView(BaseEmailView):
    """Email Attachments View
    """
    email_template = ViewPageTemplateFile("templates/email_template.pt")

    def get_recipients(self, ar):
        """Returns the recipients the results report must be send to:
        To: client's e-mail (not the contact's e-mail)
        CC: Without CC
        """
        client = ar.getClient()
        email = client.getEmailAddress()
        if not email:
            return []
        return [{
            "UID": "",
            "Fullname": client.Title(),
            "EmailAddress": email,
            "PublicationModes": ("email", "pdf",),
        }]
