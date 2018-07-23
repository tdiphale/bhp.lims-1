# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

import logging
from zope.i18nmessageid import MessageFactory

# Defining a Message Factory for when this product is internationalized.
bhpMessageFactory = MessageFactory('bhp')

logger = logging.getLogger('bhp')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing BHP LIMS Customization Package ***")
