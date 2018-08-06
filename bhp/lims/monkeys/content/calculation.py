# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)
#
import string
import traceback
from bhp.lims import logger

_marker = object()

def calculate_result(self, mapping=None, default=_marker):
    """Calculate the result
    """
    if mapping is None:
        mapping = {}
    formula = self.getMinifiedFormula()
    formula = string.Template(formula).safe_substitute(mapping)
    formula = formula.replace("[", "%(").replace("]", ")")

    try:
        formula = formula.format(**mapping)
    except KeyError:
        pass

    try:
        result = eval(formula, self._getGlobals())
    except (TypeError, ZeroDivisionError, KeyError, ImportError) as e:
        if default is _marker:
            raise e
        logger.warn(traceback.print_exc())
        return default
    return result
