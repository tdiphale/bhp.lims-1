# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

## Script (Python) "guard_deliver"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from bhp.lims.workflow.guards import guard_deliver
return guard_deliver(context)
