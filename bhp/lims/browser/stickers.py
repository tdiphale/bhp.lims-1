# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bika.lims.browser.stickers import Sticker as BaseSticker
from Products.CMFPlone.utils import safe_unicode
import re

class Sticker(BaseSticker):

    def __init__(self, context, request):
        BaseSticker.__init__(self, context, request)

    def __call__(self):
        # TODO HACK better to replace stickers preview.pt and add zebra button
        if self.request.form.get('pdf') == '1':
            # Generate the sticker in zpl format
            # https://www.zebra.com/us/en/support-downloads/knowledge-articles/using-zpl-stored-formats.html
            zpl = self.generate_zpl()
            if zpl:
               return zpl
        return BaseSticker.__call__(self)

    def generate_zpl(self):
        """Returns a stream in ZPL (Zebra Printer Label) format and sets the
        header of the response accordingly
        """
        html = self.request.form.get('html')
        matches = re.findall(r'\[ZPL-FORMAT\](.*?)\[/ZPL-FORMAT\]', html, flags=re.DOTALL)
        if not matches:
            return None
        matches = map(lambda item: item.strip(), matches)
        zpl = '\n'.join(matches)
        response = self.request.response
        response.setHeader('Content-type', 'application/octet-stream')
        response.setHeader('Content-Disposition', 'attachment; filename="sticker.zpl"')
        return safe_unicode(zpl).encode('utf-8')
