# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import DateTime


def before_transition_handler(instance, event):
    now = DateTime.DateTime()
    instance.setModificationDate(now)
