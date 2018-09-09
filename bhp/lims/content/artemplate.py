from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IARTemplate
from zope.component import adapts
from zope.interface import implements


class ARTemplateSchemaModifier(object):
    adapts(IARTemplate)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context


    def fiddle(self, schema):
        field = schema["Partitions"]
        if 'SampleType' in field.subfields:
            # TODO: For some reason, this function gets called three times!
            return schema

        field = schema["Partitions"]
        field.subfields += ('SampleType', 'sampletype_uid')
        field.subfield_labels['SampleType'] = _('SampleType')
        field.subfield_sizes['SampleType'] = 35,
        field.subfield_hidden["sampletype_uid"] = True
        field.subfield_hidden["Preservation"] = True
        field.default[0]['SampleType'] = ""
        field.default[0]["sampletype_uid"] = ""
        field.widget.combogrid_options['SampleType'] = {
            'colModel': [
                {'columnName': 'sampletype_uid', 'hidden': True},
                {'columnName': 'SampleType', 'width': '30',
                 'label': _('SampleType')},
                {'columnName': 'Description', 'width': '70',
                 'label': _('Description')}],
            'url': 'getsampletypes',
            'showOn': True,
            'width': '550px'
        }
        return schema
