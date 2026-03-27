import pytest
from django.urls import reverse
from django.test import Client
from modules.accountingEntry.models import AccountingEntry
from modules.accountingMovement.models import AccountingMovement
from modules.ledgerAccount.models import LedgerAccount
import datetime

@pytest.fixture
def ledger_account():
    return LedgerAccount.objects.create(code='1.1.01', name='Cash')

@pytest.fixture
def accounting_entry():
    return AccountingEntry.objects.create(
        date=datetime.date.today(),
        description='Test Entry',
        entry_number='TEST-001'
    )

@pytest.mark.django_db
class TestAccountingMovementModel:
    def test_movement_creation(self, accounting_entry, ledger_account):
        movement = AccountingMovement.objects.create(
            accounting_entry=accounting_entry,
            ledger_account=ledger_account,
            debit=100.00,
            credit=0.00
        )
        assert movement.debit == 100.00
        assert str(movement) == f"{accounting_entry.id} | {ledger_account.code} | D:100.0 H:0.0"

    def test_movement_relationship(self, accounting_entry, ledger_account):
        movement = AccountingMovement.objects.create(
            accounting_entry=accounting_entry,
            ledger_account=ledger_account,
            debit=0.00,
            credit=100.00
        )
        assert movement in accounting_entry.movements.all()

@pytest.mark.django_db
class TestAccountingMovementViews:
    def test_movement_list_view_success(self, client, accounting_entry, ledger_account):
        # Create a couple of movements
        AccountingMovement.objects.create(
            accounting_entry=accounting_entry,
            ledger_account=ledger_account,
            debit=100.00,
            credit=0.00
        )
        AccountingMovement.objects.create(
            accounting_entry=accounting_entry,
            ledger_account=ledger_account,
            debit=0.00,
            credit=100.00
        )

        url = reverse('accounting_movement_list', kwargs={'entry_id': accounting_entry.id})
        response = client.get(url)

        assert response.status_code == 200
        assert 'movements' in response.context
        assert len(response.context['movements']) == 2
        assert response.context['accounting_entry'] == accounting_entry
        # Check if the template is used
        assert 'partials/entry_movements.html' in [t.name for t in response.templates]

    def test_movement_list_view_404(self, client):
        url = reverse('accounting_movement_list', kwargs={'entry_id': 9999})
        response = client.get(url)
        assert response.status_code == 404
