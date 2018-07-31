# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bhp.lims.workflow import events
from bhp.lims.workflow.guards import guard_send_to_lab
from bika.lims import PMF
from bika.lims.browser.analysisrequest.workflow import \
    AnalysisRequestWorkflowAction as BaseAnalysisRequestWorkflowAction
from bika.lims.browser.client.workflow import ClientWorkflowAction
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.workflow import AfterTransitionEventHandler as _after
from bika.lims.workflow import skip


def AfterTransitionEventHandler(instance, event):
    # there is no transition for the state change (creation doesn't have a
    # 'transition')
    if not event.transition:
        return

    function_name = "after_{}".format(event.transition.id)
    if not hasattr(events, function_name):
        # Use default's After Transition Event Handler
        _after(instance, event)
        return

    # Set the request variable preventing cascade's from re-transitioning.
    if skip(instance, event.transition.id):
        return

    # Call the after_* function from events package
    getattr(events, function_name)(instance)


class SampleARWorkflowAction(BaseAnalysisRequestWorkflowAction):
    """Workflow action that applies for an AnalysisRequest or a Sample
    """
    def workflow_action_send_to_lab(self):
        """Redirects the user to the requisition form automatically generated
         due to the send_to_lab transition
        """
        logger.info("SampleARWorkflowAction.workflow_action_send_to_lab")
        action, came_from = self._get_form_workflow_action()
        trans, dest = self.submitTransition(action, came_from, [self.context])
        if trans:
            message = PMF('Changes saved.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            # TODO Page does not get refreshed when displaying pdf
            #self.destination_url = '{}/workflow_action?workflow_action=download_requisition'\
            #    .format(self.context.absolute_url())
            self.destination_url = self.context_absolute_url()
            self.request.response.redirect(self.destination_url)
        else:
            return

    def workflow_action_download_requisition(self):
        if ISample.providedBy(self.context):
            # TODO, Concatenate the PDFs of all ocntaine ARs
            logger.info("This is a sample!")

        elif IAnalysisRequest.providedBy(self.context):
            # Redirect to the requisition PDF
            req_att = self.get_last_requisition_attachment(self.context)
            if not req_att:
                return

            self.destination_url = '{}/at_download/AttachmentFile'.format(req_att.absolute_url())
            self.request.response.redirect(self.destination_url)

    def get_last_requisition_attachment(self, analysis_request):
        last_requisition_attachment = None
        attachments = analysis_request.getAttachment()
        for attachment in attachments:
            att_type = attachment.getAttachmentType()
            if not att_type:
                continue
            if att_type.Title() == 'Requisition':
                last_requisition_attachment = attachment
        return last_requisition_attachment

class SampleWorkflowAction(SampleARWorkflowAction):
    """Workflow action button clicked inside Sample"""
    pass

class AnalysisRequestWorkflowAction(SampleARWorkflowAction):
    """ Workflow action button clicked inside Analysis Request
    """
    pass



class SamplesWorkflowAction(ClientWorkflowAction):
    """ Workflow action button clicked in Samples folder list """
    pass

class AnalysisRequestsWorkflowAction(ClientWorkflowAction):
    """ Workflow action button clicked in AR folder list """
    pass
