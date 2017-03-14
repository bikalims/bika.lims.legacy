# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import App

from bika.lims import logger
from bika.lims.workflow import skip


def AfterTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    debug_mode = App.config.getConfiguration().debug_mode
    if not debug_mode:
        return

    if not skip(instance, event.transition.id, peek=True):
        logger.debug("Started transition %s on %s" %
                    (event.transition.id, instance))
##    else:
##        logger.info("Ignored transition %s on %s" %
##                    (event.transition.id, instance))
