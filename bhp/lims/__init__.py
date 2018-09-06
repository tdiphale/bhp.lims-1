# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

import logging

from AccessControl import allow_module
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import ContentInit
from zope.i18nmessageid import MessageFactory

from config import PRODUCT_NAME

# Defining a Message Factory for when this product is internationalized.
bhpMessageFactory = MessageFactory('bhp')

logger = logging.getLogger(PRODUCT_NAME)

allow_module('AccessControl')
allow_module('bhp.lims')
allow_module('bika.lims')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing BHP LIMS Customization Package ***")

    from content.courier import Courier # noqa
    from content.couriers import Couriers # noqa

    from bhp.lims.content.barcodeprinter import BarcodePrinter  # noqa
    from bhp.lims.controlpanel.barcodeprinters import BarcodePrinters # noqa

    types = listTypes(PRODUCT_NAME)
    content_types, constructors, ftis = process_types(types, PRODUCT_NAME)

    # Register each type with it's own Add permission
    # use ADD_CONTENT_PERMISSION as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PRODUCT_NAME, atype.portal_type)
        ContentInit(kind,
                    content_types=(atype,),
                    permission=AddPortalContent,
                    extra_constructors=(constructor, ),
                    fti=ftis,
                    ).initialize(context)
