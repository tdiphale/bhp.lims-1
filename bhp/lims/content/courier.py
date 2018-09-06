# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from AccessControl import ClassSecurityInfo
from bhp.lims.config import PRODUCT_NAME
from bhp.lims.interfaces import ICourier
from bika.lims.content.person import Person
from Products.Archetypes.public import registerType
from zope.interface import implements

schema = Person.schema.copy()

# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False


class Courier(Person):
    """Defines a Courier for Shipment
    """
    implements(ICourier)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Courier, PRODUCT_NAME)
