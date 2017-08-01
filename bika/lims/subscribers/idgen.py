# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.idserver import renameAfterCreation


def rename_after_creation(obj, event):
    """Rename with the IDServer
    """
    renameAfterCreation(obj)
