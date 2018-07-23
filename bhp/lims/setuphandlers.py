# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bhp.lims import bhpMessageFactory as _
from bhp.lims.config import PRODUCT_NAME


def setupHandler(context):
    """BHP setup handler
    """

    if context.readDataFile('bhp.lims.txt') is None:
        return

    logger.info("BHP setup handler [BEGIN]")

    portal = context.getSite()

    # Run installers
    setupLaboratory(portal)
    setupIDFormatting(portal)


    logger.info("BHP setup handler [DONE]")


def setupLaboratory(portal):
    """Setup Laboratory
    """
    logger.info("*** Setup Laboratory ***")
    lab = portal.bika_setup.laboratory
    lab.edit(title=_('BHP'))
    lab.reindexObject()


def setupIDFormatting(portal):
    """Setup default ID formatting
    """
    logger.info("*** Setup ID Formatting ***")
    bs = portal.bika_setup

    def set_format(format):
        if 'portal_type' not in format:
            return
        logger.info("Applying format {} for {}".format(format.get('form',''),
                                                       format.get('portal_type')))
        portal_type = format['portal_type']
        ids = list()
        id_map = bs.getIDFormatting()
        for record in id_map:
            if record.get('portal_type', '') == portal_type:
                continue
            ids.append(record)
        ids.append(format)
        bs.setIDFormatting(ids)

    # Patient ID format
    set_format(dict(form='P{seq:08d}',
                    portal_type='Patient',
                    prefix='patient',
                    sequence_type='generated',
                    split_length=1,
                    value=''))

    # Sample ID format
    set_format(dict(form='{seq:06d}',
                    portal_type='Sample',
                    prefix='sample',
                    sequence_type='generated',
                    split_length=1,
                    value=''))

    # Analysis Request ID format
    set_format(dict(form='{sampleId}R{seq:d}',
                    portal_type='AnalysisRequest',
                    counter_reference='AnalysisRequestSample',
                    counter_type='backreference',
                    sequence_type='counter',
                    value=''))
