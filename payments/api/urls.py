from django.urls import path
from . import views

urlpatterns = [
    path('receipts/', views.ReceiptListView.as_view(), name='api_receipts_list'),
    path('receipts/submit/', views.ReceiptCreateView.as_view(), name='api_receipt_submit'),
]
