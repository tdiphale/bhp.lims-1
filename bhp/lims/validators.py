# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from bhp.lims import logger
from bhp.lims import bhpMessageFactory as _
from bika.lims import api
from bika.lims import bikaMessageFactory as _b
from bika.lims.validators import \
    AnalysisSpecificationsValidator as BaseValidator
from bika.lims.validators import get_record_value
from zope.interface import implements


class AnalysisSpecificationsValidator(BaseValidator):
    """Min panic value must be below min value
       Max panic value must be above max value
       Values must be numbers
    """

    implements(IValidator)
    name = "bhp_analysisspecs_validator"

    def validate_service(self, request, uid):
        """Validates the specs values from request for the service uid. Returns
        a non-translated message if the validation failed.
        """
        logger.info("Validating......")
        message = BaseValidator.validate_service(self, request, uid)
        if message:
            # Somehow, failed a validation for one or more of the default
            # range fields (min, max, error, warn_min, warn_max)
            return message

        spec_min = get_record_value(request, uid, "min")
        spec_max = get_record_value(request, uid, "max")
        min_panic = get_record_value(request, uid, "minpanic")
        max_panic = get_record_value(request, uid, "maxpanic")

        # minpanic must be below min and below maxpanic
        if not min_panic and not max_panic:
            # Neither min_panic nor max_panic values are set, dismiss
            return None

        if min_panic:
            if not api.is_floatable(min_panic):
                return _b("'{}' value must be numeric or empty").format(_("Min panic"))
            if api.to_float(min_panic) > api.to_float(spec_min):
                return _b("'{}' value must be below '{}").format(_("Min panic"), _("Min"))

        if max_panic:
            if not api.is_floatable(min_panic):
                return _b("'{}' value must be numeric or empty").format(_("Max panic"))
            if api.to_float(min_panic) > api.to_float(spec_max):
                return _b("'{}' value must be above '{}").format(_("Max panic"), _("Max"))

        return None


validation.register(AnalysisSpecificationsValidator())