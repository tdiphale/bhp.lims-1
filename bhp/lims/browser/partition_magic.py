# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PartitionMagicView(BrowserView):
    """Manage Partitions of primary ARs
    """
    template = ViewPageTemplateFile("templates/partition_magic.pt")

    def __init__(self, context, request):
        super(PartitionMagicView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()
