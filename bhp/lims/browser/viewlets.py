from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bhp.lims import api as bapi
from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from plone.app.layout.viewlets import ViewletBase


class PanicAlertViewlet(ViewletBase):
    """ Print a viewlet showing panic level alert
    """
    template = ViewPageTemplateFile("templates/panic_alert_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(PanicAlertViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view
        self.in_panic = False
        self.panic_email_sent = ""
        self.ar_uid = ""

    def render(self):
        if IAnalysisRequest.providedBy(self.context):
            self.in_panic = self.context.has_analyses_in_panic()

        if not self.in_panic:
            return ""
        self.panic_email_sent = bapi.get_field_value(instance=self.context,
                                            field_name='PanicEmailAlertSent',
                                            default=False)
        self.ar_uid = api.get_uid(self.context)
        return self.template()
