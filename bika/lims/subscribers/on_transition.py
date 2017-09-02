# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import DateTime

def after_transition_handler(instance, event):

    # creation doesn't have a 'transition'
    if event.transition is None:
        return

    now = DateTime.DateTime()
    instance.setModificationDate(now)
