# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bhp.lims.workflow import events
from bhp.lims.workflow.guards import guard_send_to_lab
from bika.lims.browser.analysisrequest.workflow import \
    AnalysisRequestWorkflowAction as BaseAnalysisRequestWorkflowAction
from bika.lims.browser.client.workflow import ClientWorkflowAction
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.workflow import skip
from bika.lims.workflow import AfterTransitionEventHandler as _after


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
        logger.info("workflow_action_send_to_lab reached")
        if ISample.providedBy(self.context):
            logger.info("This is a sample!")
        elif IAnalysisRequest.providedBy(self.context):
            logger.info("This is an AnalysisRequest")


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
