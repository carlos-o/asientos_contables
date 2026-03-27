from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, QueryDict
from .models import AccountingEntry
from .form import AccountingEntryForm, AccountingEntryFormSet

class AccountingEntryView(View):
    """
    View for accounting entries.
    """
    template_name = 'accounting_entry.html'
    
    def get(self, request, pk=None):
        """
        Get all accounting entries, or load the edit/create modal.
        """
        if pk:
            accounting_entry = AccountingEntry.objects.get(pk=pk)
            form = AccountingEntryForm(instance=accounting_entry)
            formset = AccountingEntryFormSet(instance=accounting_entry)
            response = render(request, 'partials/add-accounting-entry-modal.html', {
                'form': form,
                'formset': formset,
                'accounting_entry': accounting_entry,
            })
            response['HX-Trigger'] = 'open-modal'
            return response

        if request.headers.get('HX-Request') and not request.GET.get('add_row'):
            form = AccountingEntryForm()
            formset = AccountingEntryFormSet()
            return render(request, 'partials/add-accounting-entry-modal.html', {
                'form': form,
                'formset': formset
            })
        
        if request.GET.get('add_row'):
            formset = AccountingEntryFormSet()
            return render(request, 'partials/movement-form-row.html', {
                'form': formset.empty_form,
            })
        

        accounting_entries = AccountingEntry.objects.all().order_by('-date', '-created_at')
        context = {
            'accounting_entries': accounting_entries,
            'form': AccountingEntryForm()
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """
        Add a new accounting entry.
        """
        form = AccountingEntryForm(request.POST)
        formset = AccountingEntryFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            accounting_entry = form.save()
            formset.instance = accounting_entry
            formset.save()
            
            response = render(request, 'partials/accounting-entry-row.html', {'entry': accounting_entry})
            response['HX-Trigger'] = 'success'  
        else:
            response = render(request, 'partials/add-accounting-entry-modal.html', {
                'form': form,
                'formset': formset
            })
            response['HX-Retarget'] = '#accounting_entry_modal'
            response['HX-Reswap'] = 'outerHTML'
            response['HX-Trigger-After-Settle'] = 'fail'
        return response
