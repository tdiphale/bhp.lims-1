# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bhp.lims.config import PRODUCT_NAME
from bhp.lims.interfaces import IBarcodePrinter
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from zope.interface import implements
from bhp.lims import bhpMessageFactory as _


schema = BikaSchema.copy() + atapi.Schema((
    atapi.StringField(
        "FileName",
        default="SENAITE-${id}.lbl",
        required=True,
        # validators=("os_path_exists",),
        widget=atapi.StringWidget(
            label=_("The name of the generated label file. "
                    "You can also reference SuperModel attributes."),
            description=_(""),
        ),
    ),
    atapi.StringField(
        "PrinterPath",
        required=True,
        validators=("os_path_exists",),
        widget=atapi.StringWidget(
            size=60,
            label=_("Printer Spool Path"),
            description=_(""),
        ),
    ),
    atapi.TextField(
        "Template",
        required=True,
        validators=(),
        default_content_type="text/plain",
        allowable_content_types=("text/plain",),
        widget=atapi.TextAreaWidget(
            label=_("Barcode Template"),
            description=_(""),
        )
    ),
))

schema["title"].widget.label = _("Printer Name")
schema["title"].widget.description = ""
schema["description"].widget.description = ""
schema["description"].widget.visible = True
# schema.moveField("description", after="Template")


class BarcodePrinter(BaseContent):
    """Defines a Barcode Printer
    """
    implements(IBarcodePrinter)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


atapi.registerType(BarcodePrinter, PRODUCT_NAME)
