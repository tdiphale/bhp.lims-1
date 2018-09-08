from bika.lims.workflow import doActionFor

def _promote_transition(obj, transition_id):
    """Promotes the transition passed in to the object's parent and ancestor
    :param obj: Analysis Request for which the transition has to be promoted
    :param transition_id: Unique id of the transition
    """
    sample = obj.getSample()
    if sample:
        doActionFor(sample, transition_id)

    # Promote the transition to its parent
    parent = obj.getParentAnalysisRequest()
    if parent:
        doActionFor(parent, transition_id)
