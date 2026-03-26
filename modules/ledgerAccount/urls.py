from django.urls import path
from . import views

urlpatterns = [
    path('', views.LedgerAccountView.as_view(), name='ledger_account'),
    path('<int:pk>/', views.LedgerAccountView.as_view(), name='ledger_account_detail'),
    path('search/', views.LedgerAccountSearch, name='ledger_account_search'),
]
