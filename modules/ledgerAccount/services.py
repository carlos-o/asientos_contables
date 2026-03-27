from .models import LedgerAccount
from django.db.models import Q
from django.core.exceptions import ValidationError


def get_all_ledger_accounts(search=None):
    """
    Retorna todas las cuentas contables
    """
    if search:
        return LedgerAccount.objects.filter(Q(code__icontains=search) | Q(name__icontains=search))
    return LedgerAccount.objects.all().order_by('-created_at')

def get_ledger_account_by_id(id):
    """
    Retorna una cuenta contable por id
    """
    return LedgerAccount.objects.filter(id=id)

def delete_ledger_account(id):
    """
    Elimina una cuenta contable
    """
    ledger_account = get_ledger_account_by_id(id)
    if not ledger_account.exists():
        raise ValidationError('The ledger account could not be found')
    
    if ledger_account[0].accountingmovement_set.count() > 0:
        raise ValidationError("The ledger account cannot be deleted because it has registered movements.")
    ledger_account.delete()
    return True
