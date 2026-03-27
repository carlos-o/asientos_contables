from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from modules.accountingEntry.models import AccountingEntry

class AccountingMovementListView(ListView):
    def get(self, request, entry_id):
        accounting_entry = get_object_or_404(AccountingEntry, id=entry_id)
        movements = accounting_entry.movements.all()
        return render(request, 'partials/entry_movements.html', {
            'accounting_entry': accounting_entry,
            'movements': movements
        })

