from django import forms
from django.forms import ValidationError, inlineformset_factory
from .models import AccountingEntry
from modules.accountingMovement.models import AccountingMovement
from modules.accountingMovement.form import AccountingMovementForm
import datetime

class AccountingEntryForm(forms.ModelForm):
    date = forms.DateField(required=True, widget=forms.DateInput(attrs={
        'class': 'input input-bordered w-full',
        'type': 'date',
        'placeholder': 'Date'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'textarea textarea-bordered w-full h-24',
        'placeholder': 'Description'
    }))
    entry_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input input-bordered w-full',
        'placeholder': 'Entry Number'
    }))
    type = forms.ChoiceField(required=True, choices=AccountingEntry.EntryType.choices, widget=forms.Select(attrs={
        'class': 'select select-bordered w-full',
        'placeholder': 'Type'
    }))
    state = forms.ChoiceField(required=True, choices=AccountingEntry.EntryState.choices, widget=forms.Select(attrs={
        'class': 'select select-bordered w-full',
        'placeholder': 'State'
    }))

    def clean_date(self):
        date = self.cleaned_data.get('date')

        if date < datetime.date.today():
            raise ValidationError("The date cannot be earlier than today's date")
        
        return date

    class Meta:
        model = AccountingEntry
        fields = ['date', 'description', 'entry_number', 'type', 'state']

class BaseAccountingMovementFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        total_debit = 0
        total_credit = 0
        count = 0

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            
            debit = form.cleaned_data.get('debit', 0)
            credit = form.cleaned_data.get('credit', 0)
            
            if debit or credit:
                total_debit += debit
                total_credit += credit
                count += 1

        if count < 2:
            raise ValidationError("An accounting entry must have at least two movements.")

        if total_debit != total_credit:
            raise ValidationError(
                f"The entry is not balanced. Total Debit: {total_debit}, Total Credit: {total_credit}"
            )

AccountingEntryFormSet = inlineformset_factory(
    AccountingEntry,
    AccountingMovement,
    form=AccountingMovementForm,
    formset=BaseAccountingMovementFormSet,
    extra=1,
    can_delete=True
)