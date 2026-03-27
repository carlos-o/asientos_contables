from django import forms
from .models import AccountingMovement

class AccountingMovementForm(forms.ModelForm):
    class Meta:
        model = AccountingMovement
        fields = ['ledger_account', 'debit', 'credit']
        widgets = {
            'ledger_account': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'debit': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'credit': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
        }
