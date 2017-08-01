# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import sys
import inspect

#from generic import xml
from abaxis.vetscan import vs2
from agilent.masshunter import quantitative, masshunter
from alere.pima import beads, cd4
from beckmancoulter.access import model2
from biodrop.ulite import ulite
from eltra.cs import cs2000
from foss.fiastar import fiastar
from foss.winescan import auto
from foss.winescan import ft120
from horiba.jobinyvon import icp
from lifetechnologies.qubit import qubit
from myself import myinstrument
from nuclisens import easyq
from panalytical.omnia import axios_xrf
from rigaku.supermini import wxrf
from rochecobas.taqman import model48
from rochecobas.taqman import model96
from scilvet.abc import plus
from eltra.cs import cs2000
from rigaku.supermini import wxrf
from myself import myinstrument
from nuclisens import easyq
from shimadzu.icpe import multitype
from shimadzu.gcms import qp2010se
from shimadzu.nexera import LC2040C, LCMS8050
from sealanalytical.aq2 import aq2
from shimadzu.gcms import tq8030
from sysmex.xs import i500, i1000
from tescan.tima import tima
from thermoscientific.arena import xt20
from thermoscientific.gallery import Ts9861x
from thermoscientific.multiskan import go
from thermoscientific.qtegra import qtegra

__all__ = ['abaxis.vetscan.vs2',
           'agilent.masshunter.quantitative',
           'agilent.masshunter.masshunter',
           'alere.pima.beads',
           'alere.pima.cd4',
           'beckmancoulter.access.model2',
           'biodrop.ulite.ulite',
           'eltra.cs.cs2000',
           'foss.fiastar.fiastar',
           'foss.winescan.auto',
           'foss.winescan.ft120',
           #'generic.xml',
           'horiba.jobinyvon.icp',
           'lifetechnologies.qubit.qubit',
           'myself.myinstrument',
           'nuclisens.easyq',
           'panalytical.omnia.axios_xrf',
           'rigaku.supermini.wxrf',
           'rochecobas.taqman.model48',
           'rochecobas.taqman.model96',
           'scilvet.abc.plus',
           'sealanalytical.aq2.aq2',
           'shimadzu.gcms.tq8030',
           'sysmex.xs.i500',
           'sysmex.xs.i1000',
           'tescan.tima.tima',
           'thermoscientific.arena.xt20',
           'thermoscientific.gallery.Ts9861x',
           'thermoscientific.multiskan.go',
           'thermoscientific.qtegra.qtegra',
           'myself.myinstrument',
           'nuclisens.easyq',
           'shimadzu.icpe.multitype',
           'shimadzu.gcms.qp2010se',
           'shimadzu.nexera.LC2040C',
           'shimadzu.nexera.LCMS8050',
           ]


def getExim(exim_id):
    currmodule = sys.modules[__name__]
    members = [obj for name, obj in inspect.getmembers(currmodule) \
               if hasattr(obj, '__name__') \
               and obj.__name__.endswith(exim_id)]
    return members[0] if len(members)>0 else None
