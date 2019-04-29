# This file is part of bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from csv import reader
import os

from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Not, Eval, Bool
from trytond.wizard import Button, StateView, Wizard, StateTransition
from trytond.transaction import Transaction
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Bank', 'LoadBanksStart', 'LoadBanks']


class Bank(metaclass=PoolMeta):
    __name__ = 'bank'
    bank_code = fields.Char('National Code', select=1,
        states={
            'required': Not(Bool(Eval('bic')))
            }, depends=['bic'])

    @classmethod
    def __setup__(cls):
        super(Bank, cls).__setup__()
        cls.party.context.update({
                'active_test': False,
                })

    @classmethod
    def search_rec_name(cls, name, clause):
        domain = super(Bank, cls).search_rec_name(name, clause)
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            domain,
            ('party',) + tuple(clause[1:]),
            ('bic',) + tuple(clause[1:]),
            ('bank_code',) + tuple(clause[1:]),
            ]


class LoadBanksStart(ModelView):
    '''Load Banks Start'''
    __name__ = 'load.banks.start'


class LoadBanks(Wizard):
    '''Load Banks'''
    __name__ = "load.banks"

    start = StateView('load.banks.start',
        'bank_es.load_banks_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Accept', 'accept', 'tryton-ok', default=True),
            ])
    accept = StateTransition()

    def transition_accept(self):
        def get_subdivision(code):
            subdividion = {
                '01': 'ES-VI',
                '02': 'ES-AB',
                '03': 'ES-A',
                '04': 'ES-AL',
                '05': 'ES-AV',
                '06': 'ES-BA',
                '07': 'ES-IB',
                '08': 'ES-B',
                '09': 'ES-BU',
                '10': 'ES-CC',
                '11': 'ES-CA',
                '12': 'ES-CS',
                '13': 'ES-CR',
                '14': 'ES-CO',
                '15': 'ES-C',
                '16': 'ES-CU',
                '17': 'ES-GI',
                '18': 'ES-GR',
                '19': 'ES-GU',
                '20': 'ES-SS',
                '21': 'ES-H',
                '22': 'ES-HU',
                '23': 'ES-J',
                '24': 'ES-LE',
                '25': 'ES-L',
                '26': 'ES-LO',
                '27': 'ES-LU',
                '28': 'ES-M',
                '29': 'ES-MA',
                '30': 'ES-MU',
                '31': 'ES-NA',
                '32': 'ES-OU',
                '33': 'ES-O',
                '34': 'ES-P',
                '35': 'ES-GC',
                '36': 'ES-PO',
                '37': 'ES-SA',
                '38': 'ES-TF',
                '39': 'ES-S',
                '40': 'ES-SG',
                '41': 'ES-SE',
                '42': 'ES-SO',
                '43': 'ES-T',
                '44': 'ES-TE',
                '45': 'ES-TO',
                '46': 'ES-V',
                '47': 'ES-VA',
                '48': 'ES-BI',
                '49': 'ES-ZA',
                '50': 'ES-Z',
                '51': 'ES-CE',
                '52': 'ES-ML',
                }
            return subdividion.get(code, None)

        pool = Pool()
        Lang = pool.get('ir.lang')
        lang, = Lang.search([('code', '=', 'es')])
        Bank = pool.get('bank')
        Party = pool.get('party.party')
        Identifier = pool.get('party.identifier')
        Address = pool.get('party.address')
        Country = pool.get('country.country')
        country, = Country.search([('code', '=', 'ES')])
        Contact = pool.get('party.contact_mechanism')
        Subdivision = pool.get('country.subdivision')
        transaction = Transaction()

        delimiter = ','
        quotechar = '"'

        def get_rows():
            with open(os.path.join(os.path.dirname(__file__), 'bank.csv'), 'r',
                    encoding='utf-8') as data:
                try:
                    rows = list(reader(data, delimiter=delimiter,
                        quotechar=quotechar))
                except TypeError as e:
                    raise UserError(gettext('bank_es.read_error',
                        filename='bank.csv', error=e))
                return rows[1:]
        created_parties = {}
        for row in get_rows():
            if not row:
                continue

            with transaction.set_context(active_test=False):
                parties = Party.search(['OR',
                        ('name', '=', row[4]),
                        ('code', '=', 'BNC' + row[1])
                        ])
            if parties:
                party = parties[0]
            else:
                party = Party()
                party.active = False
                party.name = row[4]
                party.code = 'BNC' + row[1]
                party.addresses = []
                party.lang = lang
                party.addresses = []
                party.identifiers = []
                party.contact_mechanisms = []
            if row[6]:
                codes = set([c.code for c in party.identifiers])
                vat_code = 'ES%s' % row[6]
                if vat_code not in codes:
                    identifier = Identifier()
                    identifier.type = 'eu_vat'
                    identifier.code = vat_code
                    party.identifiers = [identifier] + list(party.identifiers)

            addresses = set([a.name for a in party.addresses])
            if party.name not in addresses:
                address = Address()
                address.active = False
                address.name = party.name
                address.street = row[8]
                address.zip = row[11]
                address.city = row[12]
                address.country = country
                subdivisions = Subdivision.search([
                        ('code', '=', get_subdivision(row[14])),
                        ], limit=1)
                if subdivisions:
                    address.subdivision, = subdivisions
                party.addresses = [address] + list(party.addresses)

            new_mechanisms = []
            current_mechanisms = set([(c.type, c.value)
                    for c in party.contact_mechanisms])
            if row[16] and ('phone', row[16]) not in current_mechanisms:
                contact = Contact()
                contact.type = 'phone'
                contact.value = row[16]
                if row[16].startswith('0'):
                    contact.value = row[16][1:]
                new_mechanisms.append(contact)

            if row[18] and ('fax', row[18]) not in current_mechanisms:
                contact = Contact()
                contact.type = 'fax'
                contact.value = row[18]
                if row[18].startswith('0'):
                    contact.value = row[18][1:]
                new_mechanisms.append(contact)

            if (row[19] and ('website',
                        row[19].lower()) not in current_mechanisms):
                contact = Contact()
                contact.type = 'website'
                contact.value = row[19].lower()
                new_mechanisms.append(contact)
            if new_mechanisms:
                party.contact_mechanisms = (new_mechanisms +
                    list(party.contact_mechanisms))
            created_parties[row[1]] = party
        Party.save(list(created_parties.values()))

        to_save = []
        for row in get_rows():
            if not row:
                continue
            banks = Bank.search([('bank_code', '=', row[1])])
            if not banks:
                bank = Bank(party=None, bank_code=None, bic=None)
            else:
                bank = banks[0]
            party = created_parties[row[1]]
            if bank.party != party:
                bank.party = party
            if bank.bank_code != row[1]:
                bank.bank_code = row[1]
            if bank.bic != row[47]:
                bank.bic = row[47]
            to_save.append(bank)
        Bank.save(to_save)
        return 'end'
