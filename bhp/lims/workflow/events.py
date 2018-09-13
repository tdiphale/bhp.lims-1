# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
from Products.CMFPlone.utils import _createObjectByType
from bhp.lims import api as _api
from bhp.lims import logger
from bhp.lims.browser.requisition import generate_requisition_pdf
from bika.lims import api
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest, ISample, IProxyField, \
    IAnalysis, IDuplicateAnalysis
from bika.lims.utils import tmpID
from bika.lims.utils.samplepartition import create_samplepartition
from bika.lims.workflow import doActionFor
from bika.lims.workflow.sample import events as sample_events
from bika.lims.workflow.analysis import events as analysis_events


def _promote_transition(obj, transition_id):
    sample = obj.getSample()
    if sample:
        doActionFor(sample, transition_id)

    parent_ar = obj.getPrimaryAnalysisRequest()
    if parent_ar:
        doActionFor(parent_ar, transition_id)


def _cascade_transition(obj, transition_id):
    derived_ars = obj.getDescendants()
    for ar in derived_ars:
        doActionFor(ar, transition_id)

def _promote_cascade(obj, transition_id):
    _promote_transition(obj, transition_id)
    _cascade_transition(obj, transition_id)


def after_no_sampling_workflow(obj):
    """ Event fired for no_sampling_workflow that makes the status of the
    Analysis request or Sample to become sample_ordered
    """
    logger.info("*** Custom after_no_sampling_workflow (order) transition ***")

    # Generate the requisition report
    if IAnalysisRequest.providedBy(obj):

        # Transition Analyses to sample_due
        ans = obj.getAnalyses(full_objects=True, cancellation_state='active')
        for analysis in ans:
            doActionFor(analysis, 'no_sampling_workflow')

        # Promote to sample
        sample = obj.getSample()
        if sample:
            doActionFor(sample, 'no_sampling_workflow')

        # Generate the delivery pdf
        generate_requisition_pdf(obj)

        # Set specifications by default
        sample_type = obj.getSampleType()
        specs = _api.get_field_value(sample_type,
                                     "DefaultAnalysisSpecifications", None)
        if specs:
            obj.setSpecification(api.get_object(specs))
        else:
            # Find out suitable specs by Sample Type name
            sample_type = obj.getSampleType().Title()
            specs_title = "{} - calculated".format(sample_type)
            query = dict(portal_type="AnalysisSpec", title=specs_title)
            specs = api.search(query, 'bika_setup_catalog')
            if specs:
                obj.setSpecification(api.get_object(specs[0]))

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'no_sampling_workflow')


def after_send_to_lab(obj):
    """ Event fired after send_to_lab transition is triggered.
    """
    logger.info("*** Custom after_send_to_lab transition ***")

    if IAnalysisRequest.providedBy(obj):

        # Promote to sample
        sample = obj.getSample()
        if sample:
            doActionFor(sample, 'send_to_lab')

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'send_to_lab')


def after_deliver(obj):
    """ Event fired after delivery transition is triggered.
    """
    logger.info("*** Custom after_deliver transition ***")

    if IAnalysisRequest.providedBy(obj):
        # Promote to sample
        sample = obj.getSample()
        if sample:
            doActionFor(sample, 'deliver')

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'deliver')


def after_process(obj):
    """Event fired after process (Process) transition is triggered
    """
    logger.info("*** Custom after_process transition ***")

    if IAnalysisRequest.providedBy(obj):
        # Generate a derived AR (and Sample) for every single partition
        create_requests_from_partitions(obj)

    elif ISample.providedBy(obj):
        # We do not permit partitioning directly from Sample!
        # sample_events._cascade_transition(obj, 'process')
        pass


def after_send_to_pot(obj):
    """Event fired after sending to point of testing
    """
    logger.info("*** Custom after_send_to_pot transition ***")
    if IAnalysisRequest.providedBy(obj):
        # Transition Analyses to sample_due
        ans = obj.getAnalyses(full_objects=True, cancellation_state='active')
        for analysis in ans:
            doActionFor(analysis, 'sample_due')

        # Promote to parent AR
        _promote_cascade(obj, "send_to_pot")

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'send_to_pot')


def after_receive(obj):
    """Event fired after receive (Process) transition is triggered
    """
    logger.info("*** Custom after_receive transition ***")

    if IAnalysisRequest.providedBy(obj):

        # Transition Analyses to sample_due
        ans = obj.getAnalyses(full_objects=True, cancellation_state='active')
        for analysis in ans:
            doActionFor(analysis, 'receive')

        # Promote to parent AR
        _promote_cascade(obj, "receive")

    elif ISample.providedBy(obj):
        sample_events._cascade_transition(obj, 'receive')


def after_submit(obj):
    """Event fired after submit transition is triggered
    """
    logger.info("*** Custom after_submit transition ***")
    if IAnalysis.providedBy(obj) or IDuplicateAnalysis.providedBy(obj):
        analysis_events.after_submit(obj)

    if IAnalysisRequest.providedBy(obj):
        _promote_transition(obj, "submit")


def after_verify(obj):
    """Event fired after receive (Process) transition is triggered
    """
    logger.info("*** Custom after_verify transition ***")
    if IAnalysis.providedBy(obj):
        analysis_events.after_verify(obj)

    if IAnalysisRequest.providedBy(obj):
        _promote_transition(obj, "verify")


def after_publish(obj):
    """Event fired after receive (Process) transition is triggered
    """
    logger.info("*** Custom after_publish transition ***")
    if IAnalysisRequest.providedBy(obj):
        # Transition Analyses to sample_due
        ans = obj.getAnalyses(full_objects=True)
        for analysis in ans:
            doActionFor(analysis, 'publish')

        # Promote to parent AR
        parent_ar = obj.getPrimaryAnalysisRequest()
        if parent_ar:
            doActionFor(parent_ar, "publish")


def create_requests_from_partitions(analysis_request):
    """If more than one SamplePartition is set for the given AnalysisRequest,
    creates a new internal AR for every single SamplePartition, assign the
    primary sample to children and removes the analyses from the primary AR.
    """
    logger.info("*** Creating new requests from partitions ***")
    partitions = analysis_request.getPartitions()
    if len(partitions) < 2:
        # Only one partition, do not create new requests
        return list()

    created = list()
    client = analysis_request.getClient()
    primary_sample = analysis_request.getSample()
    primary_sample_uid = api.get_uid(primary_sample)

    ar_proxies = analysis_request.Schema().fields()
    ar_proxies = filter(lambda field: IProxyField.providedBy(field), ar_proxies)
    ar_proxies = map(lambda field: field.getName(), ar_proxies)
    skip_fields = ["Client", "Sample", "PrimarySample", "Template", "Profile",
                   "Profiles", "Analyses", "ParentAnalysisRequest",
                   "PrimaryAnalysisRequest", "RejectionReasons", "Remarks"]
    skip_fields.extend(ar_proxies)
    for part in partitions:
        analyses = part.getAnalyses()
        analyses = map(lambda an: api.get_object(an), analyses)

        # Create the new derivative sample (~partition)
        field_values = dict(PrimarySample=primary_sample_uid, InternalUse=True)
        sample_copy = copy(primary_sample, container=client,
                           new_field_values=field_values)
        #sample_copy.id = part.id
        sample_uid = api.get_uid(sample_copy)

        # Create a new Analysis Request for this Sample and analyses
        field_values = dict(Sample=sample_uid, Analyses=analyses,
                            PrimaryAnalysisRequest=analysis_request)
        ar_copy = copy(analysis_request, container=client,
                       skip_fields=skip_fields, new_field_values=field_values)

        # Create sample partition
        services = map(lambda an: an.getAnalysisService(), analyses)
        partition = dict(services=services,
                         part_id="{}-P1".format(sample_copy.getId()))
        create_samplepartition(sample_copy, partition, analyses)

        # Force all items to be in received state
        force_receive(ar_copy)

        created.append(ar_copy)
    return created


def force_receive(analysis_request):
    actions = ["no_sampling_workflow",
               "send_to_lab",
               "deliver",
               "send_to_poc",
               "receive"]
    for action in actions:
        doActionFor(analysis_request, action)


def copy(source, container, skip_fields=None, new_field_values=None):
    if new_field_values is None:
        new_field_values = dict()
    source = api.get_object(source)
    logger.info("Creating copy of {} with id {}".format(source.portal_type, source.id))
    destination = _createObjectByType(source.portal_type, container, tmpID())
    field_values = to_dict(source, skip_fields=skip_fields)
    for field_name, field_value in field_values.items():
        _api.set_field_value(destination, field_name, field_value)
    for field_name, field_value in new_field_values.items():
        _api.set_field_value(destination, field_name, field_value)
    destination.unmarkCreationFlag()
    renameAfterCreation(destination)
    destination.reindexObject()
    return destination


def to_dict(brain_or_object, skip_fields=None):
    if skip_fields is None:
        skip_fields = list()
    brain_or_object = api.get_object(brain_or_object)
    out = {}
    fields = brain_or_object.Schema().fields()
    for field in fields:
        fieldname = field.getName()
        if fieldname not in skip_fields:
            value = _api.get_field_value(brain_or_object, fieldname)
            out[fieldname] = value
    return out