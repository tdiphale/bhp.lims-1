# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest, ISamplePartition, ISample

# This is required to authorize AccessControl.ZopeGuards to access to this
# module and function/s via skin's python scripts.
from AccessControl.SecurityInfo import ModuleSecurityInfo
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
    if "Client" not in user.getRoles():
        return False

    # Only contacts from the client the Sample belongs to
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

    return True


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