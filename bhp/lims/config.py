# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
from Products.Archetypes.utils import DisplayList

PRODUCT_NAME = "bhp.lims"

GENDERS = DisplayList((
    ('m', "Male"),
    ('f', "Female"),
))

GENDERS_ANY = DisplayList((
    ('a', "Any"),
    ('m', "Male"),
    ('f', "Female"),
))

PRIORITIES = DisplayList((
    ('1', 'Urgent'),
    ('3', 'Routine'),
    ('5', 'STAT'),
))
