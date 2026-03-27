from django import forms
from django.forms import ValidationError
from .models import LedgerAccount


class LedgerAccountForm(forms.ModelForm):
    code = forms.CharField(required=True, max_length=20, 
            widget=forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Account Code'
            })
    )
    name = forms.CharField(required=True, max_length=200, 
            widget=forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Account name'
            })
    )
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={ 
                'style': 'resize: none;',
                'class': 'textarea textarea-bordered w-full h-24',
                'placeholder': 'Account description'}))

    
    def clean_code(self):
        code = self.cleaned_data['code']
        if LedgerAccount.objects.filter(code=code).exists():
            raise ValidationError('Code exists, please try another one')
        return code

    class Meta:
        model = LedgerAccount
        fields = ['code', 'name', 'description']


class LedgerAccountEditForm(forms.ModelForm):
    code = forms.CharField(required=True, max_length=20, 
            widget=forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Account Code'
            })
    )
    name = forms.CharField(required=True, max_length=200, 
            widget=forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Account name'
            })
    )
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={ 
                'style': 'resize: none;',
                'class': 'textarea textarea-bordered w-full h-24',
                'placeholder': 'Account description'}))

    def clean_code(self):
        code = self.cleaned_data['code']
        qs = LedgerAccount.objects.filter(code=code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Code exists, please try another one')
        return code

    class Meta:
        model = LedgerAccount
        fields = ['code', 'name', 'description']