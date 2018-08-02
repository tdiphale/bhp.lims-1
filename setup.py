# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from setuptools import setup, find_packages

version='1.0.0'

setup(name='bhp.lims',
      version=version,
      description="Botswana Harvard Partnership LIMS",
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bhp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'senaite.core',
          'pyBarcode'
      ],
      entry_points="""
          # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
          """,
)
