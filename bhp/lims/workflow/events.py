# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bhp.lims.browser.requisition import generate_requisition_pdf
from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.workflow import doActionFor
from bika.lims.workflow.sample import events as sample_events


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

        # Generate the requisition pdf
        generate_requisition_pdf(obj)

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'send_to_lab')
