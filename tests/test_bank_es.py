# This file is part of the bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.error import UserError
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

    @with_transaction()
    def test_spanish_ccc_validation(self):
        'Spanish CCC Number'
        pool = Pool()
        Party = pool.get('party.party')
        Bank = pool.get('bank')
        Account = pool.get('bank.account')

        party = Party(name='Test')
        party.save()
        bank = Bank(party=party, bank_code='BNK')
        bank.save()
        with self.assertRaises(UserError):
            Account.create([{
                        'bank': bank.id,
                        'numbers': [('create', [{
                                        'type': 'es_ccc',
                                        'number': '1234-1234-00 1234567890',
                                        }])],
                        }])

    @with_transaction()
    def test_spanish_ccc_number(self):
        'Spanish CCC Number'
        pool = Pool()
        Party = pool.get('party.party')
        Bank = pool.get('bank')
        Account = pool.get('bank.account')

        party = Party(name='Test')
        party.save()
        bank = Bank(party=party, bank_code='BNK')
        bank.save()
        account, = Account.create([{
                    'bank': bank.id,
                    'numbers': [('create', [{
                                    'type': 'es_ccc',
                                    'number': '21000418400200051331',
                                    }])],
                    }])

        iban_number, es_number = account.numbers
        self.assertEqual(es_number.number_compact, '21000418400200051331')
        self.assertEqual(es_number.number, '2100 0418 40 02000 51331')
        self.assertEqual(iban_number.number_compact,
            'ES4021000418400200051331')

        account, = Account.create([{
                    'bank': bank.id,
                    'numbers': [('create', [{
                                    'type': 'other',
                                    'number': '21000418400200051331',
                                    }])],
                    }])

        # Test not created until es_ccc
        number, = account.numbers
        number.type = 'es_ccc'
        number.save()
        iban_number, es_number = account.numbers
        # Test iban not duplicated
        account, = Account.create([{
                    'bank': bank.id,
                    'numbers': [('create', [{
                                    'type': 'es_ccc',
                                    'number': '21000418400200051331',
                                    }, {
                                    'type': 'iban',
                                    'number': 'ES4021000418400200051331',
                                    }])],
                    }])

        iban_number, es_number = account.numbers


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        BankEsTestCase))
    return suite
