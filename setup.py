# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import os
from setuptools import setup, find_packages

version = '3.3.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read() + "\n"

setup(name='bika.lims',
      version=version,
      description="Bika LIMS",
      long_description=read("README.rst") + \
                       read("docs/INSTALL.rst") + \
                       read("docs/CHANGELOG.txt") + \
                       "\n\n" + \
                       "Authors and maintainers\n" + \
                       "-----------------------\n" + \
                       "- Bika Lab Systems, http://bikalabs.com\n" + \
                       "- Naralabs, http://naralabs.com\n" + \
                       "- RIDING BYTES, http://ridingbytes.com",
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Intended Audience :: Information Technology",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
      ],
      keywords=['lims', 'bika', 'opensource'],
      author='Bika Laboratory Systems',
      author_email='support@bikalabs.com',
      maintainer='RIDING BYTES',
      maintainer_email='hello@ridingbytes.com',
      url='http://www.bikalims.org',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'CairoSVG==1.0.20',
          'collective.js.jqueryui',
          'collective.monkeypatcher',
          'collective.progressbar',
          'five.pt',
          'gpw',
          'jarn.jsi18n==0.3',
          'magnitude',
          'openpyxl==1.5.8',
          'plone.api',
          'plone.app.dexterity',
          'plone.app.iterate',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.app.z3cform',
          'plone.jsonapi.core',
          'plone.resource',
          'Products.AdvancedQuery',
          'Products.ATExtensions>=1.1a3',
          'Products.CMFEditions',
          'Products.DataGridField',
          'Products.TinyMCE',
          'setuptools',
          'WeasyPrint==0.19.2',
          'z3c.jbot',
          'z3c.unconfigure==1.0.1',
      ],
      extras_require={
          'test': [
              'Products.SecureMailHost',
              'plone.app.robotframework',
              'plone.app.testing',
              'plone.app.textfield',
              'plone.resource',
              'Products.PloneTestCase',
              'robotframework-debuglibrary',
              'robotframework-selenium2library',
              'robotsuite',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
