import pytest
from django.core.exceptions import ValidationError
from modules.ledgerAccount.models import LedgerAccount
from modules.ledgerAccount import services
from modules.ledgerAccount.forms import LedgerAccountForm, LedgerAccountEditForm

@pytest.mark.django_db
class TestLedgerAccountModel:
    def test_ledger_account_creation(self):
        account = LedgerAccount.objects.create(
            code="101",
            name="Caja",
            description="Cuenta de efectivo"
        )
        assert account.code == "101"
        assert account.name == "Caja"
        assert str(account) == "101 - Caja"

    def test_unique_code_constraint(self):
        LedgerAccount.objects.create(code="101", name="Caja")
        with pytest.raises(Exception): # Django raises IntegrityError usually
            LedgerAccount.objects.create(code="101", name="Banco")

@pytest.mark.django_db
class TestLedgerAccountServices:
    @pytest.fixture
    def setup_accounts(self):
        LedgerAccount.objects.create(code="101", name="Caja")
        LedgerAccount.objects.create(code="102", name="Banco")
        LedgerAccount.objects.create(code="201", name="Proveedores")

    def test_get_all_ledger_accounts(self, setup_accounts):
        accounts = services.get_all_ledger_accounts()
        assert accounts.count() == 3

    def test_get_all_ledger_accounts_search(self, setup_accounts):
        # Search by code
        accounts = services.get_all_ledger_accounts(search="101")
        assert accounts.count() == 1
        assert accounts.first().name == "Caja"

        # Search by name
        accounts = services.get_all_ledger_accounts(search="Banco")
        assert accounts.count() == 1
        assert accounts.first().code == "102"

    def test_get_ledger_account_by_id(self, setup_accounts):
        account = LedgerAccount.objects.get(code="101")
        found = services.get_ledger_account_by_id(account.id).first()
        assert found == account

    def test_delete_ledger_account_success(self, setup_accounts):
        account = LedgerAccount.objects.get(code="101")
        result = services.delete_ledger_account(account.id)
        assert result is True
        assert not LedgerAccount.objects.filter(code="101").exists()

    def test_delete_ledger_account_not_found(self):
        with pytest.raises(ValidationError, match="The ledger account could not be found"):
            services.delete_ledger_account(999)

@pytest.mark.django_db
class TestLedgerAccountViews:
    def test_ledger_account_list_view(self, client):
        response = client.get('/') 
        assert response.status_code == 200
        assert 'ledger.html' in [t.name for t in response.templates]

    def test_ledger_account_create_hx_request(self, client):
        response = client.get('/', HTTP_HX_REQUEST='true')
        assert response.status_code == 200
        assert 'partials/add-ledger-modal.html' in [t.name for t in response.templates]

    def test_ledger_account_post_success(self, client):
        data = {
            'code': '301',
            'name': 'Capital Social',
            'description': 'Capital inicial'
        }
        response = client.post('/', data)
        assert response.status_code == 200
        assert LedgerAccount.objects.filter(code='301').exists()
        assert response['HX-Trigger'] == 'success'

    def test_ledger_account_post_invalid(self, client):
        data = {'code': '', 'name': ''}
        response = client.post('/', data)
        assert response.status_code == 200
        assert response['HX-Trigger-After-Settle'] == 'fail'

    def test_ledger_account_put_success(self, client):
        account = LedgerAccount.objects.create(code="101", name="Caja")
        data = 'code=101-NEW&name=Caja+Updated'
        response = client.put(f'/{account.id}/', data=data, content_type='application/x-www-form-urlencoded')
        assert response.status_code == 200
        account.refresh_from_db()
        assert account.code == "101-NEW"
        assert response['HX-Trigger'] == 'ledger-updated'

    def test_ledger_account_delete_success(self, client):
        account = LedgerAccount.objects.create(code="101", name="Caja")
        response = client.delete(f'/{account.id}/')
        assert response.status_code == 204
        assert not LedgerAccount.objects.filter(id=account.id).exists()
        assert response['HX-Trigger'] == 'ledger-deleted'

    def test_ledger_account_search_view(self, client):
        LedgerAccount.objects.create(code="101", name="Caja")
        response = client.get('/search/?search=Caja')
        assert response.status_code == 200
        assert 'Caja' in response.content.decode()
