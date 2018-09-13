# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest, ISamplePartition, ISample

# This is required to authorize AccessControl.ZopeGuards to access to this
# module and function/s via skin's python scripts.
from AccessControl.SecurityInfo import ModuleSecurityInfo
from bika.lims.workflow import isBasicTransitionAllowed, isActive, \
    getCurrentState, wasTransitionPerformed

security = ModuleSecurityInfo(__name__)

@security.public
def guard_send_to_lab(context):
    """ Guard for send_to_lab transition. Returns true if the current user is
    a client contact, the Sample (context) is active and it belongs to the same
    client.
    """
    sample = get_sample(context)
    if not sample:
        return False

    # If Sample is inactive, we cannot send the sample to the lab
    if not api.is_active(sample):
        return False

    # Only users from role Client can send the sample to the lab
    user = api.get_current_user()
    user_roles = user.getRoles()
    # Only contacts from the client the Sample belongs to
    if "Client" in user_roles:
        client = sample.aq_parent
        if not client.getContactFromUsername(user.id):
            return False

    return True


@security.public
def guard_deliver(context):
    """Guard for deliver transition. Returns true if a Courier has been 
    assigned to the Sample and the Sample (context) is active. Note we
    do not check for roles or client here because permissions for clients
    when the sample is in state `sample_shipped` are already defined in the
    workflow definition.
    """
    sample = get_sample(context)
    if not sample:
        return False

    # If sample is inactive, we cannot deliver the sample to the lab
    if not api.is_active(sample):
        return False

    # If sample does not have a courier assigned, we cannot deliver
    if not sample.Schema()['Courier'].get(sample):
        return False

    # If the current user is a Client contact, do not allow to deliver
    user = api.get_current_user()
    if "Client" in user.getRoles():
        return False

    return True


@security.public
def guard_process(context):
    """Guard for process (partitioning) process
    Only Primary Analysis Requests can be partitioned
    """
    sample = get_sample(context)
    if not sample:
        return False

    if not api.is_active(sample):
        return False

    # If the sample is not a primary sample, do not allow processing
    if sample.Schema()['PrimarySample'].get(sample):
        return False

    return True


@security.public
def guard_send_to_pot(context):
    """Guard for sending the sample to the point of testing
    """
    return api.is_active(context)


@security.public
def guard_submit(context):
    if not IAnalysisRequest.providedBy(context):
        # Note that this guard is only used for bika_ar_workflow!
        return True

    logger.info("*** Custom Guard: submit **")
    if not isBasicTransitionAllowed(context):
        return False

    invalid = 0
    analyses = context.getAnalyses()
    for an in analyses:
        if an.review_state == 'to_be_verified':
            continue

        # The analysis has already been verified?
        an = api.get_object(an)
        if wasTransitionPerformed(an, 'submit'):
            continue

        # Maybe the analysis is in an 'inactive' state?
        if not isActive(an):
            invalid += 1
            continue

        # Maybe the analysis has been rejected or retracted?
        dettached = ['rejected', 'retracted', 'attachments_due']
        status = getCurrentState(an)
        if status in dettached:
            invalid += 1
            continue

        # At this point we can assume this analysis is an a valid state and
        # the AR could potentially be submitted, but the Analysis Request can
        # only be submitted if all the analyses have been submitted already
        return False

    # Be sure that at least there is one analysis in an active state, it
    # doesn't make sense to submit an Analysis Request if all the analyses that
    # contains are rejected or cancelled!
    return len(analyses) - invalid > 0


def get_sample(instance):
    """Returns the sample associated to this instance, if any. Otherwise,
    returns None"""
    if ISample.providedBy(instance):
        return instance
    if IAnalysisRequest.providedBy(instance):
        return get_sample(instance.getSample())
    if ISamplePartition.providedBy(instance):
        return get_sample(instance.aq_parent)
    return None