# This file is part bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.bank_es.tests.test_bank_es import suite
except ImportError:
    from .test_bank_es import suite

__all__ = ['suite']
