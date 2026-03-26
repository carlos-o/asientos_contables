from .models import LedgerAccount
from django.db.models import Q
from django.core.exceptions import ValidationError


def get_all_ledger_accounts(search=None):
    if search:
        return LedgerAccount.objects.filter(Q(code__icontains=search) | Q(name__icontains=search))
    return LedgerAccount.objects.all().order_by('-created_at')

def get_ledger_account_by_id(id):
    return LedgerAccount.objects.filter(id=id)

def update_ledger_account(id, data):
    ledger_account = LedgerAccount.objects.get(id=id)
    for field, value in data.items():
        setattr(ledger_account, field, value)
    ledger_account.save()
    return ledger_account

def delete_ledger_account(id):
    ledger_account = get_ledger_account_by_id(id)
    if not ledger_account.exists():
        raise ValidationError('No se encontro la cuenta contable')
    
    # if ledger_account.movimientos.exists():
    #     raise ValidationError("No se puede eliminar: esta cuenta tiene movimientos registrados.")
    ledger_account.delete()
    return True
