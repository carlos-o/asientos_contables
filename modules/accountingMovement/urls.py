from django.urls import path
from .views import AccountingMovementListView

urlpatterns = [
    path('<int:entry_id>/', AccountingMovementListView.as_view(), name='accounting_movement_list'),
]
