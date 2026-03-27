from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountingEntryView.as_view(), name='accounting_entry'),
    path('<int:pk>/', views.AccountingEntryView.as_view(), name='accounting_entry_detail'),
]