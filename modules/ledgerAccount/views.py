from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, QueryDict
from . import services 
from .forms import LedgerAccountForm, LedgerAccountEditForm

class LedgerAccountView(View):
    """
    View for ledger accounts.
    """
    template_name = 'ledger.html'
    
    def get(self, request, pk=None):
        """
        Get all ledger accounts, or load the edit/create modal.
        """
        if pk:
            ledger_account = services.get_ledger_account_by_id(pk).first()
            form = LedgerAccountEditForm(instance=ledger_account)
            response = render(request, 'partials/add-ledger-modal.html', {
                'form': form,
                'ledger_account': ledger_account,
            })
            response['HX-Trigger'] = 'open-modal'
            return response

        if request.headers.get('HX-Request'):
            form = LedgerAccountForm()
            return render(request, 'partials/add-ledger-modal.html', {'form': form})

        context = {
            'ledger_accounts': services.get_all_ledger_accounts(),
            'form': LedgerAccountForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """
        Add a new ledger account.
        """
        form = LedgerAccountForm(request.POST)
        if form.is_valid():
            ledger_account = form.save()
            response = render(request, 'partials/ledger-row.html', {'ledger': ledger_account})
            response['HX-Trigger'] = 'success'  
        else:
            response = render(request, 'partials/add-ledger-modal.html', {'form': form})
            response['HX-Retarget'] = '#ledger_modal'
            response['HX-Reswap'] = 'outerHTML'
            response['HX-Trigger-After-Settle'] = 'fail'
        return response
    
    def put(self, request, pk):
        """
        Update a ledger account.
        """
        
        data = QueryDict(request.body)
        ledger_account = services.get_ledger_account_by_id(pk).first()
        form = LedgerAccountEditForm(data, instance=ledger_account)
        if form.is_valid():
            updated = form.save()
            response = render(request, 'partials/ledger-row.html', {'ledger': updated})
            response['HX-Trigger'] = 'ledger-updated'
        else:
            response = render(request, 'partials/add-ledger-modal.html', {
                'form': form,
                'ledger_account': ledger_account,
            })
            response['HX-Retarget'] = '#ledger_modal'
            response['HX-Reswap'] = 'outerHTML'
            response['HX-Trigger-After-Settle'] = 'fail'
        return response

    def delete(self, request, pk):
        """
        Delete a ledger account.
        """
        try:
            services.delete_ledger_account(pk)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'ledger-deleted'
        except Exception as e:
            response = render(request, 'errors.html', {'error': str(e)})
            response.status_code = 400
            response['HX-Reswap'] = 'outerHTML'
        return response

def LedgerAccountSearch(request):
    """
    Search for ledger accounts by code or name.
    """
    search = request.GET.get('search')
    ledger_accounts = services.get_all_ledger_accounts(search)
    return render(request, 'partials/ledger-account-list.html', {'ledger_accounts': ledger_accounts})
