# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bhp.lims.browser.delivery import generate_delivery_pdf
from bhp.lims.browser.requisition import generate_requisition_pdf
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.workflow import doActionFor
from bika.lims.workflow.sample import events as sample_events

def after_no_sampling_workflow(obj):
    """ Event fired for no_sampling_workflow that makes the status of the
    Analysis request or Sample to become sample_ordered
    """
    logger.info("*** Custom after_no_sampling_workflow (order) transition ***")

    # Generate the requisition report
    if IAnalysisRequest.providedBy(obj):

        # Transition Analyses to sample_due
        ans = obj.getAnalyses(full_objects=True, cancellation_state='active')
        for analysis in ans:
            doActionFor(analysis, 'no_sampling_workflow')

        # Promote to sample
        sample = obj.getSample()
        if sample:
            doActionFor(sample, 'no_sampling_workflow')

        # Generate the delivery pdf
        generate_requisition_pdf(obj)

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'no_sampling_workflow')


def after_send_to_lab(obj):
    """ Event fired after send_to_lab transition is triggered.
    """
    logger.info("*** Custom after_send_to_lab transition ***")

    if IAnalysisRequest.providedBy(obj):

        # Transition Analyses to sample_due
        ans = obj.getAnalyses(full_objects=True, cancellation_state='active')
        for analysis in ans:
            doActionFor(analysis, 'sample_due')

        # Promote to sample
        sample = obj.getSample()
        if sample:
            doActionFor(sample, 'send_to_lab')

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'send_to_lab')

        # Generate the delivery pdf
        generate_delivery_pdf(obj)


def after_deliver(obj):
    """ Event fired after delivery transition is triggered.
    """
    logger.info("*** Custom after_deliver transition ***")

    if IAnalysisRequest.providedBy(obj):

        # Promote to sample
        sample = obj.getSample()
        if sample:
            doActionFor(sample, 'deliver')

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'deliver')
