from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Loan
from django.db import models

@login_required
@login_required
def take_book(request, book_id):
    from books.models import Book

    book = get_object_or_404(Book, id=book_id)

    # Проверяем, нет ли у пользователя уже этой книги
    existing_loan = Loan.objects.filter(book_id=book_id, user=request.user, status='active').first()
    if existing_loan:
        messages.warning(request, 'У вас уже есть эта книга')
        return redirect('book_detail', book_id=book_id)

    # Создаем запись о выдаче
    from django.utils import timezone
    from datetime import timedelta

    loan = Loan.objects.create(
        book_id=book_id,
        user=request.user,
        status='active',
        expiry_date=timezone.now() + timedelta(days=book.max_loan_days)
    )

    messages.success(request, f'Книга "{book.title}" успешно добавлена в вашу библиотеку!')
    return redirect('book_detail', book_id=book_id)

@login_required
def my_loans(request):
    loans = Loan.objects.filter(user=request.user).order_by('-loan_date')

    from books.models import Book
    loan_data = []
    for loan in loans:
        try:
            book = Book.objects.get(id=loan.book_id)
            loan_data.append({
                'loan': loan,
                'book': book
            })
        except Book.DoesNotExist:
            continue

    return render(request, 'loans/my_loans.html', {'loan_data': loan_data})
