# This file is part bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import bank


def register():
    Pool.register(
        bank.Bank,
        bank.LoadBanksStart,
        module='bank_es', type_='model')
    Pool.register(
        bank.LoadBanks,
        module='bank_es', type_='wizard')
