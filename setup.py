# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from setuptools import setup, find_packages

version="1.0.0"

setup(
    name="bhp.lims",
    version=version,
    description="Botswana Harvard Partnership LIMS",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["bhp"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "archetypes.schemaextender",
        "pyBarcode",
        "senaite.core.supermodel>=1.0.0",
        "senaite.core>=1.2.8",
        "senaite.lims>=1.2.2",
        "setuptools",
    ],
    extras_require={
        "test": [
            "Products.PloneTestCase",
            "plone.app.testing",
            "unittest2",
        ]
    },
    entry_points="""
          # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
          """,
)
