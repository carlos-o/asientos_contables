import pytest
from django.urls import reverse
from django.forms import ValidationError
from modules.accountingEntry.models import AccountingEntry
from modules.accountingMovement.models import AccountingMovement
from modules.ledgerAccount.models import LedgerAccount
from modules.accountingEntry.form import AccountingEntryForm, AccountingEntryFormSet
import datetime

@pytest.fixture
def ledger_account_1():
    return LedgerAccount.objects.create(code='1.1.01', name='Cash')

@pytest.fixture
def ledger_account_2():
    return LedgerAccount.objects.create(code='4.1.01', name='Sales')

@pytest.mark.django_db
class TestAccountingEntryModel:
    def test_accounting_entry_creation(self):
        entry = AccountingEntry.objects.create(
            date=datetime.date.today(),
            description='Test Entry',
            entry_number='ENTRY-001'
        )
        assert str(entry) == "ENTRY-001 | Test Entry"
        assert entry.total_debit == 0
        assert entry.total_credit == 0
        assert entry.is_balanced is True

    def test_balanced_entry_movements(self, ledger_account_1, ledger_account_2):
        entry = AccountingEntry.objects.create(
            date=datetime.date.today(),
            description='Balanced Entry'
        )
        AccountingMovement.objects.create(accounting_entry=entry, ledger_account=ledger_account_1, debit=100, credit=0)
        AccountingMovement.objects.create(accounting_entry=entry, ledger_account=ledger_account_2, debit=0, credit=100)
        
        assert entry.total_debit == 100
        assert entry.total_credit == 100
        assert entry.is_balanced is True

    def test_unbalanced_entry_movements(self, ledger_account_1, ledger_account_2):
        entry = AccountingEntry.objects.create(
            date=datetime.date.today(),
            description='Unbalanced Entry'
        )
        AccountingMovement.objects.create(accounting_entry=entry, ledger_account=ledger_account_1, debit=100, credit=0)
        AccountingMovement.objects.create(accounting_entry=entry, ledger_account=ledger_account_2, debit=0, credit=50)
        
        assert entry.total_debit == 100
        assert entry.total_credit == 50
        assert entry.is_balanced is False

@pytest.mark.django_db
class TestAccountingEntryForms:
    def test_entry_form_past_date(self):
        form_data = {
            'date': datetime.date.today() - datetime.timedelta(days=1),
            'description': 'Past Date Entry',
            'entry_number': 'PAST-001',
            'type': 'JO',
            'state': 'DR'
        }
        form = AccountingEntryForm(data=form_data)
        assert form.is_valid() is False
        assert 'date' in form.errors
        assert form.errors['date'][0] == "The date cannot be earlier than today's date"

    def test_formset_balance_validation(self, ledger_account_1, ledger_account_2):
        entry = AccountingEntry.objects.create(date=datetime.date.today())
        data = {
            'movements-TOTAL_FORMS': '2',
            'movements-INITIAL_FORMS': '0',
            'movements-MIN_NUM_FORMS': '0',
            'movements-MAX_NUM_FORMS': '1000',
            'movements-0-ledger_account': ledger_account_1.id,
            'movements-0-debit': '100.00',
            'movements-0-credit': '0.00',
            'movements-1-ledger_account': ledger_account_2.id,
            'movements-1-debit': '0.00',
            'movements-1-credit': '50.00', # Unbalanced
        }
        formset = AccountingEntryFormSet(data=data, instance=entry, prefix='movements')
        assert formset.is_valid() is False
        assert formset.non_form_errors()[0].startswith("The entry is not balanced")

    def test_formset_min_movements_validation(self, ledger_account_1):
        entry = AccountingEntry.objects.create(date=datetime.date.today())
        data = {
            'movements-TOTAL_FORMS': '1',
            'movements-INITIAL_FORMS': '0',
            'movements-0-ledger_account': ledger_account_1.id,
            'movements-0-debit': '100.00',
            'movements-0-credit': '100.00', 
        }
        formset = AccountingEntryFormSet(data=data, instance=entry, prefix='movements')
        assert formset.is_valid() is False
        assert formset.non_form_errors()[0] == "An accounting entry must have at least two movements."

@pytest.mark.django_db
class TestAccountingEntryViews:
    def test_get_entry_list(self, client):
        response = client.get(reverse('accounting_entry'))
        assert response.status_code == 200
        assert 'accounting_entries' in response.context
        assert 'accounting_entry.html' in [t.name for t in response.templates]

    def test_get_entry_modal_htmx(self, client):
        response = client.get(reverse('accounting_entry'), HTTP_HX_REQUEST='true')
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'formset' in response.context
        assert 'partials/add-accounting-entry-modal.html' in [t.name for t in response.templates]

    def test_post_valid_entry(self, client, ledger_account_1, ledger_account_2):
        data = {
            'date': datetime.date.today().strftime('%Y-%m-%d'),
            'description': 'Valid Post Entry',
            'entry_number': 'VALID-001',
            'type': 'JO',
            'state': 'DR',
            'movements-TOTAL_FORMS': '2',
            'movements-INITIAL_FORMS': '0',
            'movements-0-ledger_account': ledger_account_1.id,
            'movements-0-debit': '100.00',
            'movements-0-credit': '0.00',
            'movements-1-ledger_account': ledger_account_2.id,
            'movements-1-debit': '0.00',
            'movements-1-credit': '100.00',
        }
        response = client.post(reverse('accounting_entry'), data=data)
        assert response.status_code == 200
        assert AccountingEntry.objects.filter(entry_number='VALID-001').exists()
        entry = AccountingEntry.objects.get(entry_number='VALID-001')
        assert entry.movements.count() == 2
        assert response['HX-Trigger'] == 'success'

    def test_post_invalid_balanced(self, client, ledger_account_1, ledger_account_2):
        data = {
            'date': datetime.date.today().strftime('%Y-%m-%d'),
            'description': 'Invalid Balance Post',
            'entry_number': 'INVALID-001',
            'type': 'JO',
            'state': 'DR',
            'movements-TOTAL_FORMS': '2',
            'movements-INITIAL_FORMS': '0',
            'movements-0-ledger_account': ledger_account_1.id,
            'movements-0-debit': '100.00',
            'movements-0-credit': '0.00',
            'movements-1-ledger_account': ledger_account_2.id,
            'movements-1-debit': '0.00',
            'movements-1-credit': '50.00',
        }
        response = client.post(reverse('accounting_entry'), data=data)
        assert response.status_code == 200
        assert not AccountingEntry.objects.filter(entry_number='INVALID-001').exists()
        assert response['HX-Trigger-After-Settle'] == 'fail'

    def test_get_edit_modal(self, client, ledger_account_1):
        entry = AccountingEntry.objects.create(date=datetime.date.today(), description="Edit Me")
        AccountingMovement.objects.create(accounting_entry=entry, ledger_account=ledger_account_1, debit=100, credit=100)
        
        response = client.get(reverse('accounting_entry_detail', kwargs={'pk': entry.pk}))
        assert response.status_code == 200
        assert response.context['accounting_entry'] == entry
        assert response['HX-Trigger'] == 'open-modal'

    def test_get_add_row(self, client):
        response = client.get(reverse('accounting_entry'), {'add_row': '1'}, HTTP_HX_REQUEST='true')
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'partials/movement-form-row.html' in [t.name for t in response.templates]
