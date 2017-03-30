# -*- coding: utf-8 -*-

import pkgutil

from bika.lims import logger
from bika.lims.jsonapi.v2 import routes

__build__ = 0
__version__ = 2
__date__ = "2017-03-30"

prefix = routes.__name__ + "."
for importer, modname, ispkg in pkgutil.iter_modules(
        routes.__path__, prefix):
    module = __import__(modname, fromlist="dummy")
    logger.info("INITIALIZED BIKA JSON API V2 ROUTE ---> %s" % module.__name__)
