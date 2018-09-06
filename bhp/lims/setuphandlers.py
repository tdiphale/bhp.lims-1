# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from Products.CMFCore.permissions import ModifyPortalContent, View, \
    AccessContentsInformation
from Products.CMFPlone.utils import _createObjectByType
from Products.DCWorkflow.Guard import Guard
from bhp.lims import api as _api
from bhp.lims import bhpMessageFactory as _
from bhp.lims import logger
from bhp.lims.specscalculations import get_xls_specifications
from bika.lims import api
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.idserver import renameAfterCreation
from bika.lims.permissions import CancelAndReinstate, EditFieldResults, \
    EditResults, EditSample, PreserveSample, ReceiveSample, ScheduleSampling
from bika.lims.utils import tmpID
from zope.annotation.interfaces import IAnnotations

AR_CONFIGURATION_STORAGE = "bika.lims.browser.analysisrequest.manage.add"

CONTROLPANELS = [
    {
        "id": "barcodeprinters",
        "type": "BarcodePrinters",
        "title": "Barcode Printers",
        "description": "",
        "insert-after": "*"
    }
]

INDEXES = [
    # Tuples of (catalog, id, indexed attribute, type)
]

COLUMNS = [
    # Tuples of (catalog, column name)
]

CATALOGS_BY_TYPE = [
    # Tuples of (type, [catalog])
    ("BarcodePrinter", ["bika_setup_catalog"]),
    ("Courier", ["bika_setup_catalog"]),
]

PRINTERS = {
    "Zebra Printer Template 1": {
        "FileName": "lims-${id}.zpl",
        "PrinterPath": "/tmp/",
        "Template":
        """^XA^PR4
^FO315,15^A0N,20,15^FD${ClientID} ${TaxNumber} ${SampleType.Prefix}^FS
^FO315,34^BY1^BCN,50,N,N,N,A
^FD${id}^FS
^FO315,92^A0N,20,15^FD${id} ${Template.title}^FS
^FO315,112^A0N,20,15^FD${ParticipantID} ${ParticipantInitials}^FS
^FO315,132^A0N,20,15^FDDOB: ${DateOfBirth|to_date} ${Gender}^FS
^FO315,152^A0N,20,15^FD${DateSampled|to_long_date}^FS
^XZ"""
        },
    }


def setupHandler(context):
    """BHP setup handler
    """

    if context.readDataFile('bhp.lims.txt') is None:
        return

    logger.info("BHP setup handler [BEGIN]")

    portal = context.getSite()

    # Run installers
    setup_laboratory(portal)

    # Add new content types
    setup_new_content_types(portal)

    # Apply ID format to content types
    setup_id_formatting(portal)

    # Sort AR fields (AR Add)
    sort_ar_fields(portal)

    # Hide unused AR Fields
    hide_unused_ar_fields(portal)

    # Setup specimen shipment (from clinic) workflow
    setup_bhp_workflow(portal)

    # Setup Attachment Types (requisition + delivery)
    setup_attachment_types(portal)

    # Update priorities to Urgent, Routine, STAT
    update_priorities(portal)

    # update analysis services (Replace % by PCT in Analysis Keywords)
    update_services(portal)

    # Update InternalUse for Samples and Analysis Requests
    update_internal_use(portal)

    # Import specifications from bhp/lims/resources/results_ranges.xlsx
    import_specifications(portal)

    # Setup Controlpanels
    setup_controlpanels(portal)

    # Setup printer stickers
    setup_printer_stickers(portal)

    # Setup Catalogs
    setup_catalogs(portal)

    logger.info("BHP setup handler [DONE]")


def setup_printer_stickers(portal):
    """Setup printers and stickers templates
    """
    logger.info("*** Setup printers and stickers ***")
    def create_printer(printer_name, portal, defaults):
        query = dict(portal_type="BarcodePrinter", Title=printer_name)
        printers = api.search(query, "bika_setup_catalog")
        if printers:
            printer = api.get_object(printers[0])
            printer.FileName = printer_values["FileName"]
            printer.PrinterPath = printer_values["PrinterPath"]
            printer.Template = printer_values["Template"]
            return printer

        # Create a new Barcode Printer
        folder = portal.bika_setup.barcodeprinters
        obj = _createObjectByType("BarcodePrinter", folder, tmpID())
        obj.edit(title=printer_name,
                 FileName=printer_values["FileName"],
                 PrinterPath=printer_values["PrinterPath"],
                 Template=printer_values["Template"])
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

    for printer_name, printer_values in PRINTERS.items():
        create_printer(printer_name, portal, printer_values)


def setup_laboratory(portal):
    """Setup Laboratory
    """
    logger.info("*** Setup Laboratory ***")
    lab = portal.bika_setup.laboratory
    lab.edit(title=_('BHP'))
    lab.reindexObject()

    # Set autoprinting of stickers on register
    portal.bika_setup.setAutoPrintStickers('register')


def setup_new_content_types(portal):
    """Setup new content types"""
    logger.info("*** Setup new content types ***")

    # Index objects - Importing through GenericSetup doesn't
    ids = ['couriers']
    for obj_id in ids:
        obj = portal.bika_setup[obj_id]
        obj.unmarkCreationFlag()
        obj.reindexObject()


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
    # Format:
    #   08502AAA01
    # Where:
    #   - 085: Client's Study ID
    #   - 02: Sample Type prefix (e.g. for Whole blood)
    #   - AAA01: Alphanumeric numbering
    set_format(dict(form='{studyId}{sampleType}{alpha:3a2d}',
                    portal_type='Sample',
                    prefix='sample',
                    sequence_type='generated',
                    split_length=2,
                    value=''))

    # Analysis Request ID format
    set_format(dict(form='{primarySampleId}{seq:02d}',
                    portal_type='AnalysisRequest',
                    prefix='sample',
                    sequence_type='generated',
                    split_length=1,
                    value=''))


def get_manage_add_storage(portal):
    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    storage = annotation.get(AR_CONFIGURATION_STORAGE)
    if storage is None:
        annotation[AR_CONFIGURATION_STORAGE] = OOBTree()
    return annotation[AR_CONFIGURATION_STORAGE]


def update_manage_add_storage(portal, storage):
    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    annotation[AR_CONFIGURATION_STORAGE] = storage

def flush_manage_add_storage(portal):
    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    if annotation[AR_CONFIGURATION_STORAGE]:
        del annotation[AR_CONFIGURATION_STORAGE]

def hide_unused_ar_fields(portal):
    """Hides unused fields from AR Add Form
    """
    logger.info("*** Hiding default fields from AR Add ***")
    field_names_to_hide = ["Sample",
                           "RejectionReasons",
                           "Specification",
                           "InternalUse"]

    storage = get_manage_add_storage(portal)
    visibility = storage.get('visibility', {}).copy()
    ordered = storage.get('order', [])
    fields = list(set(visibility.keys() + field_names_to_hide + ordered))
    for field_name in fields:
        visibility[field_name] = field_name not in field_names_to_hide
    storage.update({"visibility": visibility})
    update_manage_add_storage(portal, storage)


def sort_ar_fields(portal):
    """Sort AR fields from AR Add Form
    """
    logger.info("*** Sorting fields from AR Add ***")
    sorted=['Client',
            'Contact',
            'ParticipantID',
            'OtherParticipantReference',
            'ParticipantInitials',
            'Gender',
            'Visit',
            'DateOfBirth',
            'Fasting',
            'ClientSampleID',
            'DateSampled',
            'SampleType',
            'Volume',
            'DefaultContainerType',
            'Template',
            'OtherInformation',
            '_ARAttachment',
            'Priority',
            'Remarks',
            ]

    storage = get_manage_add_storage(portal)
    storage.update({"order": sorted})
    update_manage_add_storage(portal, storage)


def setup_bhp_workflow(portal):
    """
    Setup the shipment/delivery workflow for samples:

    1. Clinic submits the form      -- [no_sampling_wf] --> sample_ordered
    2. Clinic sends the Sample      -- [send_to_lab]    --> sample_shipped
    3. Delivery to lab              -- [deliver]        --> sample_at_reception
    4. Process Sample               -- [process]        --> sample_at_reception
    5. Send to Point of testing     -- [send_to_pot]    --> sample_due
    6. Receive at Point of Testing  -- [receive]        --> received

    """
    logger.info("*** Setting up BHP custom workflow ***")
    setup_bhp_workflow_for(portal, 'bika_sample_workflow')
    setup_bhp_workflow_for(portal, 'bika_ar_workflow')

    def update_objects(query, catalog):
        """Bind the workflow changes to the objects previously created
        """
        brains = api.search(query, catalog)
        for brain in brains:
            update_role_mappings(brain)

    # We rebind the affected workflows to the objects previously created in the
    # system. Although not strictly necessary in a fresh instance, this is
    # interesting for pilot testing. Once stable, this will not be required
    # anymore and eventual changes in workflow will be done in upgrade steps.
    review_states = ['sample_ordered', 'sample_shipped', 'sample_at_reception',
                     'sample_due']
    portal_types = ['AnalysisRequest', 'Sample', 'SamplePartition']
    query = dict(review_state=review_states, portal_type=portal_types)
    # Analysis Requests live in its own catalog, Samples and Partitions live
    # either in portal_catalog and bika_catalog
    update_objects(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    update_objects(query, 'bika_catalog')

    # Update couriers (we want Clients to have access to them)
    update_objects(dict(portal_type='Courier'), 'portal_catalog')


def setup_bhp_workflow_for(portal, workflow_id):
    wtool = api.get_tool("portal_workflow")
    workflow = wtool.getWorkflowById(workflow_id)

    # STATUSES CREATION
    # Ordered: Clinic submits the form --[no_sampling_wf]--> sample_ordered
    sample_ordered = workflow.states.get('sample_ordered')
    if not sample_ordered:
        workflow.states.addState('sample_ordered')
        sample_ordered = workflow.states.sample_ordered
    sample_ordered.title = "Ordered"
    roles = ('Manager', 'LabManager', 'LabClerk', 'Owner')
    sample_ordered.setPermission(AccessContentsInformation, False, roles)
    sample_ordered.setPermission(ModifyPortalContent, False, roles)
    sample_ordered.setPermission(View, False, roles)
    sample_ordered.setPermission(CancelAndReinstate, False, roles)
    sample_ordered.setPermission(EditFieldResults, False, ())
    sample_ordered.setPermission(EditResults, False, ())
    sample_ordered.setPermission(EditSample, False, roles)
    sample_ordered.setPermission(PreserveSample, False, ())
    sample_ordered.setPermission(ReceiveSample, False, ())
    sample_ordered.setPermission(ScheduleSampling, False, ())
    sample_ordered.transitions = ('send_to_lab', 'reject')
    workflow.transitions.no_sampling_workflow.new_state_id = 'sample_ordered'

    # Shipped: Clinic sent the sample --[send_to_lab]--> sample_shipped
    sample_shipped = workflow.states.get('sample_shipped')
    if not sample_shipped:
        workflow.states.addState('sample_shipped')
        sample_shipped = workflow.states.sample_shipped
    sample_shipped.title = "Shipped"
    roles = ('Manager', 'LabManager', 'LabClerk', 'Owner')
    sample_shipped.setPermission(AccessContentsInformation, False, roles)
    sample_shipped.setPermission(ModifyPortalContent, False, roles)
    sample_shipped.setPermission(View, False, roles)
    sample_shipped.setPermission(CancelAndReinstate, False, roles)
    sample_shipped.setPermission(EditFieldResults, False, ())
    sample_shipped.setPermission(EditResults, False, ())
    sample_shipped.setPermission(EditSample, False, roles)
    sample_shipped.setPermission(PreserveSample, False, ())
    sample_shipped.setPermission(ReceiveSample, False, ())
    sample_shipped.setPermission(ScheduleSampling, False, ())
    sample_shipped.transitions = ('deliver', 'reject')

    # At reception: Sample is delivered --[deliver]--> sample_at_reception
    at_reception = workflow.states.get('sample_at_reception')
    if not at_reception:
        workflow.states.addState('sample_at_reception')
        at_reception = workflow.states.sample_at_reception
    at_reception.title = "At reception"
    roles = ('Manager', 'LabManager', 'LabClerk', 'Owner')
    at_reception.setPermission(AccessContentsInformation, False, roles)
    at_reception.setPermission(ModifyPortalContent, False, roles)
    at_reception.setPermission(View, False, roles)
    at_reception.setPermission(CancelAndReinstate, False, roles)
    at_reception.setPermission(EditFieldResults, False, ())
    at_reception.setPermission(EditResults, False, ())
    at_reception.setPermission(EditSample, False, roles)
    at_reception.setPermission(PreserveSample, False, ())
    at_reception.setPermission(ReceiveSample, False, ())
    at_reception.setPermission(ScheduleSampling, False, ())
    at_reception.transitions = ('send_to_pot', 'process', 'reject')

    # Process: Create partitions --[process]--> sample_at_reception
    # No new state is necessary here

    # Sent to PoT: Sample is sent to PoT --[send_to_pot]--> sample_due
    workflow.states.sample_due.title = "Sent to point of testing"

    # At Point of PoT: Sample is received at PoT --[receive]--> sample_received
    workflow.states.sample_received.title = "At point of testing"

    # TRANSITIONS CREATION
    # Send to lab: ordered --> sample_shipped
    if not workflow.transitions.get('send_to_lab'):
        workflow.transitions.addTransition('send_to_lab')
    send_transition = workflow.transitions.send_to_lab
    send_transition.setProperties(
        title='Send to Lab',
        new_state_id='sample_shipped',
        after_script_name='',
        actbox_name="Send to Lab",)
    guard_send = send_transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Add Sample',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_send_to_lab()'}
    guard_send.changeFromProperties(guard_props)
    send_transition.guard = guard_send

    # Deliver: sample_shipped --> sample_at_reception
    if not workflow.transitions.get('deliver'):
        workflow.transitions.addTransition('deliver')
    deliver_transition = workflow.transitions.deliver
    deliver_transition.setProperties(
        title="Receive at reception",
        new_state_id='sample_at_reception',
        after_script_name='',
        actbox_name="Receive at reception",)
    guard_deliver = deliver_transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Add Sample',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_deliver()'}
    guard_deliver.changeFromProperties(guard_props)
    deliver_transition.guard = guard_deliver

    # Process: sample_at_reception --> sample_at_reception
    if not workflow.transitions.get('process'):
        workflow.transitions.addTransition('process')
    process_transition = workflow.transitions.process
    process_transition.setProperties(
        title="Process",
        new_state_id='sample_at_reception',
        after_script_name='',
        actbox_name="Process", )
    guard_process = process_transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Add Sample',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_process()'}
    guard_process.changeFromProperties(guard_props)
    process_transition.guard = guard_process

    # Send to Pot: sample_at_reception --> sample_due
    if not workflow.transitions.get('send_to_pot'):
        workflow.transitions.addTransition('send_to_pot')
    send2pot_transition = workflow.transitions.send_to_pot
    send2pot_transition.setProperties(
        title="Send to point of testing",
        new_state_id='sample_due',
        after_script_name='',
        actbox_name="Send to point of testing", )
    guard_send2pot = send2pot_transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Add Sample',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_send_to_pot()'}
    guard_send2pot.changeFromProperties(guard_props)
    send2pot_transition.guard = guard_send2pot

    # Receive at PoT: sample_due--> sample_received
    workflow.transitions.receive.title="Receive at point of testing"
    workflow.transitions.receive.actbox_name = "Receive at point of testing"


def update_role_mappings(obj_or_brain, wfs=None, reindex=True):
    """Update the role mappings of the given object
    """
    obj = api.get_object(obj_or_brain)
    wftool = api.get_tool("portal_workflow")
    if wfs is None:
        wfs = get_workflows()
    chain = wftool.getChainFor(obj)
    for wfid in chain:
        wf = wfs[wfid]
        wf.updateRoleMappingsFor(obj)
    if reindex is True:
        obj.reindexObject(idxs=["allowedRolesAndUsers"])
    return obj


def get_workflows():
    """Returns a mapping of id->workflow
    """
    wftool = api.get_tool("portal_workflow")
    wfs = {}
    for wfid in wftool.objectIds():
        wf = wftool.getWorkflowById(wfid)
        if hasattr(aq_base(wf), "updateRoleMappingsFor"):
            wfs[wfid] = wf
    return wfs


def update_priorities(portal):
    """Reset the priorities of created ARs to those defined for BHP
    1: Urgent, 3: Routine, 5: STAT
    """
    logger.info("*** Restoring Priorities ***")
    query = dict(portal_type='AnalysisRequest')
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    for brain in brains:
        obj = api.get_object(brain)
        if obj.getPriority() == '2':
            # High --> Urgent (1)
            obj.setPriority(1)
            obj.reindexObject()
        elif obj.getPriority() == '4':
            # Low --> STAT
            obj.setPriority(5)
            obj.reindexObject()


def update_services(portal):
    logger.info("*** Updating services ***")
    for service in portal.bika_setup.bika_analysisservices.values():
        keyword = service.Schema().getField('Keyword').get(service)
        if '%' in keyword:
            keyword = keyword.replace('%', '_PCT')
            logger.info("Replaced Analysis Keyword: {}".format(keyword))
            service.setKeyword(keyword)
            service.reindexObject()


def setup_attachment_types(portal):
    """Creates two attachment types. One for requisition and another one for
    the checklist delivery report
    """
    logger.info("*** Creating custom Attachment Types ***")
    new_attachment_types = ['Requisition', 'Delivery']
    folder = portal.bika_setup.bika_attachmenttypes
    for attachment in folder.values():
        if attachment.Title() in new_attachment_types:
            new_attachment_types.remove(attachment.Title())

    atts_uids = {}
    for new_attachment in new_attachment_types:
        obj = _createObjectByType("AttachmentType", folder, tmpID())
        obj.edit(title=new_attachment,
                 description="Attachment type for {} files".format(new_attachment))
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)


    logger.info("*** Assign Attachment Types to requisition and rejection ***")
    new_attachment_types = {'Requisition': None, 'Delivery': None}
    for attachment in folder.values():
        for att_type in new_attachment_types.keys():
            if attachment.Title() == att_type:
                new_attachment_types[att_type] = attachment
                break

    query = dict(portal_type='AnalysisRequest')
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    for brain in brains:
        obj = api.get_object(brain)
        attachments = obj.getAttachment()
        for attachment in attachments:
            if attachment.getAttachmentType():
                continue
            for key, val in new_attachment_types.items():
                if key.lower() in attachment.getAttachmentFile().filename:
                    attachment.setAttachmentType(val)
                    attachment.setReportOption('i') # Ignore in report
                    break


def import_specifications(portal):
    """Creates (or updates) dynamic specifications from
    resources/results_ranges.xlsx
    """

    logger.info("*** Importing specifications ***")

    def get_bs_object(xlsx_row, xlsx_keyword, portal_type, criteria):
        text_value = xlsx_row.get(xlsx_keyword, None)
        if not text_value:
            logger.warn("Value not set for keyword {}".format(xlsx_keyword))
            return None

        query = {"portal_type": portal_type, criteria: text_value}
        brain = api.search(query, 'bika_setup_catalog')
        if not brain:
            logger.warn("No objects found for type {} and {} '{}'"
                        .format(portal_type, criteria, text_value))
            return None
        if len(brain) > 1:
            logger.warn("More than one object found for type {} and {} '{}'"
                        .format(portal_type, criteria, text_value))
            return None

        return api.get_object(brain[0])

    raw_specifications = get_xls_specifications()
    for spec in raw_specifications:

        # Valid Sample Type?
        sample_type = get_bs_object(spec, "sample_type", "SampleType", "title")
        if not sample_type:
            continue

        # Valid Analysis Service?
        service = get_bs_object(spec, "keyword", "AnalysisService", "getKeyword")
        if not service:
            continue

        # The calculation exists?
        calc_title = "Ranges calculation"
        query = dict(calculation=calc_title)
        calc = get_bs_object(query, "calculation", "Calculation", "title")
        if not calc:
            # Create a new one
            folder = portal.bika_setup.bika_calculations
            _id = folder.invokeFactory("Calculation", id=tmpID())
            calc = folder[_id]
            calc.edit(title=calc_title,
                      PythonImports=[{"module": "bhp.lims.specscalculations",
                                      "function": "get_specification_for"}],
                      Formula="get_specification_for($spec)")
            calc.unmarkCreationFlag()
            renameAfterCreation(calc)

        # Existing AnalysisSpec?
        specs_title = "{} - calculated".format(sample_type.Title())
        query = dict(portal_type='AnalysisSpec', title=specs_title)
        aspec = api.search(query, 'bika_setup_catalog')
        if not aspec:
             # Create the new AnalysisSpecs object!
             folder = portal.bika_setup.bika_analysisspecs
             _id = folder.invokeFactory('AnalysisSpec', id=tmpID())
             aspec = folder[_id]
             aspec.edit(title=specs_title)
             aspec.unmarkCreationFlag()
             renameAfterCreation(aspec)
        elif len(aspec) > 1:
            logger.warn("More than one Analysis Specification found for {}"
                        .format(specs_title))
            continue
        else:
            aspec = api.get_object(aspec[0])
        aspec.setSampleType(sample_type)

        # Set the analysis keyword and bind it to the calculation to use
        keyword = service.getKeyword()
        specs_dict = {
            'keyword': keyword,
            'min_operator': 'geq',
            'min': '0',
            'max_operator': 'lt',
            'max': '0',
            'minpanic': '',
            'maxpanic': '',
            'warn_min': '',
            'warn_max': '',
            'hidemin': '',
            'hidemax': '',
            'rangecomments': '',
            'calculation': api.get_uid(calc),
        }
        ranges = _api.get_field_value(aspec, 'ResultsRange', [{}])
        ranges = filter(lambda val: val.get('keyword') != keyword, ranges)
        ranges.append(specs_dict)
        aspec.setResultsRange(ranges)


def update_internal_use(portal):
    """Walks through all Samples and assigns its value to False if no value set
    """
    logger.info("*** Updating InternalUse field on Samples/ARs ***")
    samples = api.search(dict(portal_type="Sample"), "bika_catalog")
    for sample in samples:
        sample = api.get_object(sample)
        if _api.get_field_value(sample, "InternalUse", None) is None:
            _api.set_field_value(sample, "InternalUse", False)


def setup_controlpanels(portal):
    """Setup Plone control and Senaite management panels
    """
    logger.info("*** Setup Controlpanels ***")

    # get the bika_setup object
    bika_setup = api.get_bika_setup()
    cp = api.get_tool("portal_controlpanel")

    def get_action_index(action_id):
        if action_id == "*":
            action = cp.listActions()[-1]
            action_id = action.getId()
        for n, action in enumerate(cp.listActions()):
            if action.getId() == action_id:
                return n
        return -1

    for item in CONTROLPANELS:
        id = item.get("id")
        type = item.get("type")
        title = item.get("title")
        description = item.get("description")

        panel = bika_setup.get(id, None)
        if panel is None:
            logger.info("Creating Setup Folder '{}' in Setup.".format(id))
            # allow content creation in setup temporary
            portal_types = api.get_tool("portal_types")
            fti = portal_types.getTypeInfo(bika_setup)
            fti.filter_content_types = False
            myfti = portal_types.getTypeInfo(type)
            global_allow = myfti.global_allow
            myfti.global_allow = True
            _ = bika_setup.invokeFactory(type, id, title=title)
            panel = bika_setup[_]
            myfti.global_allow = global_allow
            fti.filter_content_types = True
        else:
            # set some meta data
            panel.setTitle(title)
            panel.setDescription(description)

        # Move configlet action to the right index
        action_index = get_action_index(id)
        ref_index = get_action_index(item["insert-after"])
        if (action_index != -1) and (ref_index != -1):
            actions = cp._cloneActions()
            action = actions.pop(action_index)
            actions.insert(ref_index + 1, action)
            cp._actions = tuple(actions)
            cp._p_changed = 1

        # reindex the object to render it properly in the navigation portlet
        panel.reindexObject()


def setup_catalogs(portal):
    """Setup Plone catalogs
    """
    logger.info("*** Setup Catalogs ***")

    # Add InstrumentDomains to the right catalogs

    # Setup catalogs by type
    for type_name, catalogs in CATALOGS_BY_TYPE:
        at = api.get_tool("archetype_tool")
        # get the current registered catalogs
        current_catalogs = at.getCatalogsByType(type_name)
        # get the desired catalogs this type should be in
        desired_catalogs = map(api.get_tool, catalogs)
        # check if the catalogs changed for this portal_type
        if set(current_catalogs).difference(desired_catalogs):
            # fetch the brains to reindex
            brains = api.search({"portal_type": type_name})
            # updated the catalogs
            at.setCatalogsByType(type_name, catalogs)
            logger.info("*** Assign '%s' type to Catalogs %s" %
                        (type_name, catalogs))
            for brain in brains:
                obj = api.get_object(brain)
                logger.info("*** Reindexing '%s'" % repr(obj))
                obj.reindexObject()

    # Setup catalog indexes
    to_index = []
    for catalog, name, attribute, meta_type in INDEXES:
        c = api.get_tool(catalog)
        indexes = c.indexes()
        if name in indexes:
            logger.info("*** Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("*** Adding Index '%s' for field '%s' to catalog ..."
                    % (meta_type, name))
        c.addIndex(name, meta_type)
        to_index.append((c, name))
        logger.info("*** Added Index '%s' for field '%s' to catalog [DONE]"
                    % (meta_type, name))

    for catalog, name in to_index:
        logger.info("*** Indexing new index '%s' ..." % name)
        catalog.manage_reindexIndex(name)
        logger.info("*** Indexing new index '%s' [DONE]" % name)

    # Setup catalog metadata columns
    for catalog, name in COLUMNS:
        c = api.get_tool(catalog)
        if name not in c.schema():
            logger.info("*** Adding Column '%s' to catalog '%s' ..."
                        % (name, catalog))
            c.addColumn(name)
            logger.info("*** Added Column '%s' to catalog '%s' [DONE]"
                        % (name, catalog))
        else:
            logger.info("*** Column '%s' already in catalog '%s'  [SKIP]"
                        % (name, catalog))
            continue
