# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims.config import PRODUCT_NAME
from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.interfaces import ISetupDataSetList
from zope.interface import implements


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname=PRODUCT_NAME)
