# This file is part of the bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class BankEsTestCase(ModuleTestCase):
    'Test Bank Es module'
    module = 'bank_es'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        BankEsTestCase))
    return suite