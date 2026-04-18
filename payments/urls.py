from django.urls import path, include
from . import views
app_name = "payments"
urlpatterns = [
path('fund/<int:job_id>/', views.fund_escrow, name='fund_escrow'),
path('release/<int:job_id>/', views.release_payment, name='release_payment'),
path('deposit/', views.deposit_money, name='deposit_money'),
]
