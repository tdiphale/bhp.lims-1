# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IClient
from zope.component import adapts
from zope.interface import implements

class ClientSchemaModifier(object):
    adapts(IClient)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        schema['TaxNumber'].widget.label = _("Study Code")
        return schema
