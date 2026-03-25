from django.db import models

# Create your models here.

class AccountingMovement(models.Model):
    accounting_entry = models.ForeignKey('accountingEntry.AccountingEntry', on_delete=models.CASCADE)
    ledger_account = models.ForeignKey('ledgerAccount.LedgerAccount', on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=19, decimal_places=2)
    credit = models.DecimalField(max_digits=19, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['accounting_entry', 'ledger_account'], name='idx_entry_account'),
            models.Index(fields=['ledger_account'], name='idx_ledger_account'),
            
        ]
        verbose_name = "Movimiento Contable"
        verbose_name_plural = "Movimientos Contables"

    def __str__(self):
        return f"{self.accounting_entry.id} | {self.ledger_account.code} | D:{self.debit} H:{self.credit}"
