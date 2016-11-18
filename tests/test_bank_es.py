# This file is part of the bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


def import_banks():
    pool = Pool()
    LoadBank = pool.get('load.banks', type='wizard')
    Country = pool.get('country.country')
    # We must create a country as country data is not loaded on tests
    if not Country.search([('code', '=', 'ES')]):
        country = Country(code='ES', name='Spain')
        country.save()
    session_id, _, _ = LoadBank.create()
    load = LoadBank(session_id)
    load.transition_accept()


class BankEsTestCase(ModuleTestCase):
    'Test Bank Es module'
    module = 'bank_es'

    @with_transaction()
    def test_import_banks(self):
        'Import Spanish Banks'
        pool = Pool()
        Bank = pool.get('bank')
        self.assertEqual(Bank.search([], count=True), 0)
        import_banks()
        banks = Bank.search([], count=True)
        self.assertGreater(banks, 0)
        # Update should not duplicate
        import_banks()
        self.assertEqual(banks, Bank.search([], count=True))


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        BankEsTestCase))
    return suite
