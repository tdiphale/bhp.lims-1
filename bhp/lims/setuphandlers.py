# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from AccessControl.Permissions import access_contents_information
from AccessControl.Permissions import view
from BTrees.OOBTree import OOBTree
from Products.CMFCore.permissions import ModifyPortalContent
from Products.DCWorkflow.Guard import Guard
from bhp.lims import bhpMessageFactory as _
from bhp.lims import logger
from bika.lims import api
from bika.lims.permissions import CancelAndReinstate, EditFieldResults, \
    EditResults, EditSample, PreserveSample, ReceiveSample, ScheduleSampling
from zope.annotation.interfaces import IAnnotations


def setupHandler(context):
    """BHP setup handler
    """

    if context.readDataFile('bhp.lims.txt') is None:
        return

    logger.info("BHP setup handler [BEGIN]")

    portal = context.getSite()

    # Run installers
    setup_laboratory(portal)

    # Apply ID format to content types
    setup_id_formatting(portal)

    # Hide unused AR Fields
    hide_unused_ar_fields(portal)

    # Sort AR fields (AR Add)
    sort_ar_fields(portal)

    # Setup specimen shipment (from clinic) workflow
    setup_shipment_workflow(portal)

    # Add additonal metadata and indexes in catalogs
    add_columns_and_indexes(portal)

    logger.info("BHP setup handler [DONE]")


def setup_laboratory(portal):
    """Setup Laboratory
    """
    logger.info("*** Setup Laboratory ***")
    lab = portal.bika_setup.laboratory
    lab.edit(title=_('BHP'))
    lab.reindexObject()


def setup_id_formatting(portal):
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


def hide_unused_ar_fields(portal):
    """Hides unused fields from AR Add Form
    """
    logger.info("*** Hiding default fields from AR Add ***")
    field_names_to_hide = ["AdHoc", "Batch", "CCContact", "CCEmails",
                           "ClientOrderNumber", "ClientReference",
                           "ClientSampleID", "Composite", "Contact",
                           "DateSampled", "DefaultContainerType",
                           "EnvironmentalConditions", "InvoiceExclude",
                           "PreparationWorkflow", "Priority", "Sample",
                           "SampleCondition", "SamplePoint", "Sampler",
                           "SamplingDate", "SamplingDeviation", "SamplingRound",
                           "Specification", "StorageLocation", "SubGroup",
                           "Template",]

    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    AR_CONFIGURATION_STORAGE = "bika.lims.browser.analysisrequest.manage.add"
    storage = annotation.get(AR_CONFIGURATION_STORAGE, OOBTree())

    visibility = storage.get('visibility', {}).copy()
    for field_name in field_names_to_hide:
        visibility[field_name] = False
    storage.update({"visibility": visibility})
    annotation[AR_CONFIGURATION_STORAGE] = storage


def sort_ar_fields(portal):
    """Sort AR fields from AR Add Form
    """
    logger.info("*** Sorting fields from AR Add ***")
    sorted=['Client', 'Contact', 'ParticipantID', 'OtherParticipantReference',
            'ParticipantInitials', 'Gender', 'Visit', 'DateOfBirth', 'Fasting',
            'DateSampled', 'SampleType', 'Volume', 'Profiles', 'OtherInformation',
            '_ARAttachment', 'CCContact', 'CCEmails', 'Sample', 'Batch',
            'SamplingRound', 'SubGroup', 'Template', 'Sampler', 'SamplingDate',
            'Specification', 'SamplePoint', 'StorageLocation',
            'ClientOrderNumber', 'ClientReference', 'ClientSampleID',
            'SamplingDeviation', 'SampleCondition', 'Priority',
            'EnvironmentalConditions', 'DefaultContainerType', 'AdHoc',
            'Composite', 'InvoiceExclude', 'PreparationWorkflow']

    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    AR_CONFIGURATION_STORAGE = "bika.lims.browser.analysisrequest.manage.add"
    storage = annotation.get(AR_CONFIGURATION_STORAGE, OOBTree())
    storage.update({"order": sorted})


def setup_shipment_workflow(portal):
    logger.info("*** Setting up shipment workflow ***")
    setup_shipment_workflow_for(portal, 'bika_sample_workflow')
    setup_shipment_workflow_for(portal, 'bika_ar_workflow')


def setup_shipment_workflow_for(portal, workflow_id):
    wtool = api.get_tool("portal_workflow")
    workflow = wtool.getWorkflowById(workflow_id)
    # Create sample_ordered state
    sample_ordered = workflow.states.get('sample_ordered')
    if not sample_ordered:
        workflow.states.addState('sample_ordered')
        sample_ordered = workflow.states.sample_ordered
    sample_ordered.title = "Sample ordered"
    roles = ('Manager', 'LabManager', 'LabClerk', 'Owner')
    sample_ordered.setPermission(access_contents_information, False, roles)
    sample_ordered.setPermission(ModifyPortalContent, False, roles)
    sample_ordered.setPermission(view, False, roles)
    sample_ordered.setPermission(CancelAndReinstate, False, roles)
    sample_ordered.setPermission(EditFieldResults, False, ())
    sample_ordered.setPermission(EditResults, False, ())
    sample_ordered.setPermission(EditSample, False, roles)
    sample_ordered.setPermission(PreserveSample, False, ())
    sample_ordered.setPermission(ReceiveSample, False, ())
    sample_ordered.setPermission(ScheduleSampling, False, ())
    sample_ordered.transitions = ('send_to_lab', 'reject')

    # The exit transition of 'no_sampling_workflow' is 'sample_ordered'
    workflow.transitions.no_sampling_workflow.new_state_id = 'sample_ordered'

    # Create the send transition (ordered --> sample_due)
    if not workflow.transitions.get('send_to_lab'):
        workflow.transitions.addTransition('send_to_lab')
    send_transition = workflow.transitions.send_to_lab
    send_transition.setProperties(
        title='Send to Lab',
        new_state_id='sample_due',
        after_script_name='',
        actbox_name="Send to Lab",
    )
    guard_send =send_transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Add Sample',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_send_to_lab()'}
    guard_send.changeFromProperties(guard_props)
    send_transition.guard = guard_send


def add_columns_and_indexes(portal):
    logger.info("*** Adding columns and indexes ***")
    pass
