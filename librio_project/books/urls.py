from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('manage/', views.manage_books, name='manage_books'),
    path('add/', views.add_book, name='add_book'),
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('book/<int:book_id>/read/', views.book_reader, name='book_reader'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),]
