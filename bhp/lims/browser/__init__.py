# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

def add_transition(listing, transition_id, review_state_ids=None):
    """Adds a transition for the review_staate ids passed in.
    If review_states are not specified, will add the transition to all them
    """
    if not review_state_ids:
        review_state_ids = map(lambda rev: rev['id'], listing.review_states)

    new_states = []
    for state in listing.review_states:
        if state['id'] in review_state_ids:
            if 'transitions' not in state:
                state['transitions']=list()
            state['transitions'].append(dict(id=transition_id))
        new_states.append(state)
    listing.review_states = new_states


def add_review_state(listing, review_state, before_id=None):
    """Adds a new review state after the one passed in
    """
    if not review_state:
        return
    if not before_id:
        listing.review_states.append(review_state)
    index = 0
    for index, state in enumerate(listing.review_states):
        if state['id'] == before_id:
            break
    listing.review_states.insert(index, review_state)


def add_column(listing, column_id, values, review_state_ids=None):
    """Adds a new column to the list"""
    if not review_state_ids:
        review_state_ids = map(lambda rev: rev['id'], listing.review_states)
    listing.columns[column_id] = values
    new_states = []
    for state in listing.review_states:
        if state['id'] in review_state_ids:
            state['columns'].append(column_id)
        new_states.append(state)
    listing.review_states = new_states
