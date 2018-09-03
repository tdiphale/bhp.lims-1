# -*- coding: utf-8 -*-

from functools import wraps

from senaite import api
from senaite.core.supermodel.interfaces import ISuperModel
from zope.component import queryAdapter


def returns_super_model(func):
    """Decorator to return standard content objects as SuperModels
    """
    def to_super_model(obj):
        # avoid circular imports
        from senaite.core.supermodel import SuperModel

        # Object is already a SuperModel
        if isinstance(obj, SuperModel):
            return obj

        # Only portal objects are supported
        if not api.is_object(obj):
            raise TypeError("Expected a portal object, got '{}'"
                            .format(type(obj)))

        # Wrap the object into a specific Publication Object Adapter
        uid = api.get_uid(obj)
        portal_type = api.get_portal_type(obj)

        adapter = queryAdapter(uid, ISuperModel, name=portal_type)
        if adapter is None:
            return SuperModel(uid)
        return adapter

    @wraps(func)
    def wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)
        if isinstance(obj, (list, tuple)):
            return map(to_super_model, obj)
        return to_super_model(obj)

    return wrapper
