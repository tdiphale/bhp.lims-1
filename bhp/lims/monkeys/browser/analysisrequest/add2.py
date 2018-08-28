# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims.setuphandlers import sort_ar_fields
from bhp.lims.setuphandlers import hide_unused_ar_fields
from bika.lims import api


def flush(self):
    """Restore the sorting and visibility of fields from AR Add form
    """
    portal = api.get_portal()
    sort_ar_fields(portal)
    hide_unused_ar_fields(portal)
