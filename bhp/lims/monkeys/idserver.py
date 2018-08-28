# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from bhp.lims import api as _api
from bika.lims.idserver import get_current_year
from bika.lims.alphanumber import Alphanumber
from bika.lims import api
from bika.lims import logger


def get_variables(context, **kw):
    """Prepares a dictionary of key->value pairs usable for ID formatting
    """

    # allow portal_type override
    portal_type = kw.get("portal_type") or api.get_portal_type(context)

    # The variables map hold the values that might get into the constructed id
    variables = {
        'context': context,
        'id': api.get_id(context),
        'portal_type': portal_type,
        'year': get_current_year(),
        'parent': api.get_parent(context),
        'seq': 0,
        'alpha': Alphanumber(0),
    }

    # Augment the variables map depending on the portal type
    if portal_type == "AnalysisRequest":
        primary_sample = _api.get_field_value(context, "PrimarySample", None)
        primary_sample = primary_sample or context.getSample()
        variables.update({
            'sampleId': context.getSample().getId(),
            'sample': context.getSample(),
            'primarySampleId': primary_sample.getId(),
        })

    elif portal_type == "SamplePartition":
        variables.update({
            'sampleId': context.aq_parent.getId(),
            'sample': context.aq_parent,
        })

    elif portal_type == "Sample":
        # get the prefix of the assigned sample type
        sample_id = context.getId()
        sample_type = context.getSampleType()
        sampletype_prefix = sample_type.getPrefix()

        date_now = DateTime()
        sampling_date = context.getSamplingDate()
        date_sampled = context.getDateSampled()

        # Try to get the date sampled and sampling date
        if sampling_date:
            samplingDate = DT2dt(sampling_date)
        else:
            # No Sample Date?
            logger.error("Sample {} has no sample date set".format(sample_id))
            # fall back to current date
            samplingDate = DT2dt(date_now)

        if date_sampled:
            dateSampled = DT2dt(date_sampled)
        else:
            # No Sample Date?
            logger.error("Sample {} has no sample date set".format(sample_id))
            dateSampled = DT2dt(date_now)

        variables.update({
            'clientId': context.aq_parent.getClientID(),
            'dateSampled': dateSampled,
            'samplingDate': samplingDate,
            'sampleType': sampletype_prefix,
            'studyId': context.aq_parent.getTaxNumber(),
        })

    elif portal_type == "ARReport":
        variables.update({
            'clientId': context.aq_parent.getClientID(),
        })

    return variables
