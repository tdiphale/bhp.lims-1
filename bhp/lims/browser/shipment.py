# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#

from bhp.lims.browser import add_review_state, add_transition


class ShipmentListingDecorator(object):

    def render(self, listing):
        # Add review state button 'sample_ordered'
        ordered_rev = {
            "id": "sample_ordered",
            "title": ("Ordered"),
            "contentFilter": {
                "review_state": ("sample_ordered",),
                "sort_on": "created",
                "sort_order": "descending"},
            "transitions": [],
            "custom_transitions": [],
            "columns": listing.columns.keys(),
        }
        ordered_rev['columns'] = listing.columns.keys()
        add_review_state(listing=listing, review_state=ordered_rev,
                         before_id='sample_due')

        # Add transition 'send_to_lab'
        add_transition(listing=listing, transition_id='send_to_lab',
                       review_state_ids=['default', 'sample_due'])
