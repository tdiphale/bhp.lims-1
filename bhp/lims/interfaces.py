# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from zope.interface import Interface
from bika.lims.interfaces import IBikaLIMS


class IBhpLIMS(IBikaLIMS):
    """Marker interface that defines a Zope 3 browser layer.
    A layer specific for this add-on product.
    This interface is referred in browserlayer.xml.
    All views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run.
    """


class ICourier(Interface):
    """The person that delivers a Sample (or AnalysisRequest) to the lab, so
    that needs to be tracked in Chain of Custody.
    """


class ICouriers(Interface):
    """Folder containing all Couriers"""
