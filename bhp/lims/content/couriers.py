# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import registerType
from bhp.lims.interfaces import ICouriers
from bhp.lims.config import PRODUCT_NAME
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Couriers(ATFolder):
    implements(ICouriers)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(Couriers, PRODUCT_NAME)
