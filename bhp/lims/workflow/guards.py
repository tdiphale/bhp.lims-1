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
    if IAnalysisRequest.providedBy(context):
        return guard_send_to_lab(context.getSample())

    if ISamplePartition.providedBy(context):
        return guard_send_to_lab(context.aq_parent)

    if not ISample.providedBy(context):
        return False

    # If Sample is inactive, we cannot send the sample to the lab
    if not api.is_active(context):
        return False

    # Only users from role Client can send the sample to the lab
    user = api.get_current_user()
    if "Client" not in user.getRoles():
        return False

    # Only contacts from the client the Sample belongs to
    client = context.aq_parent
    if not client.getContactFromUsername(user.id):
        return False

    # TODO Check if Courier assigned to the Sample
    return True
