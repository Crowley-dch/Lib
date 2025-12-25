from django.urls import path
from . import views

urlpatterns = [
    path('take/<int:book_id>/', views.take_book, name='take_book'),
    path('my-loans/', views.my_loans, name='my_loans'),
]