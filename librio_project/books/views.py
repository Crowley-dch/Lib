from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Book, Genre, Author
from users.decorators import admin_required, librarian_required
from datetime import  timedelta
from django.utils import timezone
from loans.models import Loan
from users.models import UserProfile
from django.contrib.auth.models import User
from .utils import check_book_access
def book_list(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__full_name__icontains=search_query) |
            Q(genre__name__icontains=search_query)
        )

    if genre_filter:
        books = books.filter(genre__id=genre_filter)

    return render(request, 'books/book_list.html', {
        'books': books,
        'genres': genres,
        'search_query': search_query,
        'selected_genre': genre_filter
    })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_detail.html', {'book': book})


@librarian_required
def manage_books(request):
    books = Book.objects.all().order_by('-id')

    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__full_name__icontains=search_query)
        )

    return render(request, 'books/manage_books.html', {
        'books': books,
        'search_query': search_query
    })


@librarian_required
def add_book(request):
    from .models import Author, Genre

    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author')
        genre_id = request.POST.get('genre')
        access_level = request.POST.get('access_level', 'free')
        max_loan_days = request.POST.get('max_loan_days', 14)
        description = request.POST.get('description', '')

        if title and author_id and genre_id:
            try:
                author = Author.objects.get(id=author_id)
                genre = Genre.objects.get(id=genre_id)

                Book.objects.create(
                    title=title,
                    author=author,
                    genre=genre,
                    access_level=access_level,
                    max_loan_days=max_loan_days,
                    description=description,
                    is_available=True
                )

                messages.success(request, 'Книга успешно добавлена!')
                return redirect('manage_books')

            except (Author.DoesNotExist, Genre.DoesNotExist):
                messages.error(request, 'Ошибка: автор или жанр не найден')

    authors = Author.objects.all()
    genres = Genre.objects.all()

    return render(request, 'books/add_book.html', {
        'authors': authors,
        'genres': genres
    })


@librarian_required
def edit_book(request, book_id):
    from .models import Author, Genre

    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # Обновляем данные
        book.title = request.POST.get('title')
        author_id = request.POST.get('author')
        genre_id = request.POST.get('genre')
        book.access_level = request.POST.get('access_level', 'free')
        book.max_loan_days = request.POST.get('max_loan_days', 14)
        book.description = request.POST.get('description', '')
        book.is_available = request.POST.get('is_available') == 'true'

        try:
            if author_id:
                book.author = Author.objects.get(id=author_id)
            if genre_id:
                book.genre = Genre.objects.get(id=genre_id)

            book.save()
            messages.success(request, 'Книга успешно обновлена!')
            return redirect('manage_books')

        except (Author.DoesNotExist, Genre.DoesNotExist):
            messages.error(request, 'Ошибка: автор или жанр не найден')

    # GET запрос - показываем форму с текущими данными
    authors = Author.objects.all()
    genres = Genre.objects.all()

    return render(request, 'books/edit_book.html', {
        'book': book,
        'authors': authors,
        'genres': genres
    })
@librarian_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена!')
        return redirect('manage_books')

    return render(request, 'books/delete_book.html', {'book': book})


@admin_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_users = User.objects.count()
    total_authors = Author.objects.count()

    active_loans = Loan.objects.filter(status='active').count()

    week_ago = timezone.now() - timedelta(days=7)
    loans_last_week = Loan.objects.filter(loan_date__gte=week_ago).count()

    books_by_genre = Book.objects.values('genre__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    recent_books = Book.objects.order_by('-id')[:5]

    recent_loans = Loan.objects.order_by('-loan_date')[:10]

    users_by_type = UserProfile.objects.values('user_type').annotate(
        count=Count('id')
    ).order_by('-count')

    loan_data = []
    for loan in recent_loans:
        try:
            book = Book.objects.get(id=loan.book_id)
            loan_data.append({
                'loan': loan,
                'book': book,
                'user': loan.user
            })
        except Book.DoesNotExist:
            continue

    context = {
        'total_books': total_books,
        'total_users': total_users,
        'total_authors': total_authors,
        'active_loans': active_loans,
        'loans_last_week': loans_last_week,
        'books_by_genre': books_by_genre,
        'recent_books': recent_books,
        'loan_data': loan_data,
        'users_by_type': users_by_type,
    }

    return render(request, 'books/admin_dashboard.html', context)


@login_required
@login_required
def book_reader(request, book_id):

    book = get_object_or_404(Book, id=book_id)

    if not check_book_access(book, request.user):
        messages.error(request, '❌ У вас нет доступа к этой книге')
        return redirect('book_detail', book_id=book_id)

    if not hasattr(book, 'content'):
        messages.error(request, '📭 Текст книги пока не добавлен')
        return redirect('book_detail', book_id=book_id)

    try:
        page_num = int(request.GET.get('page', 1))
    except:
        page_num = 1

    pages = book.content.split_into_pages()
    total_pages = len(pages)

    if page_num < 1:
        page_num = 1
    elif page_num > total_pages:
        page_num = total_pages


    from .utils import add_watermark
    page_content = add_watermark(
        pages[page_num - 1],
        request.user.id,
        book_id,
        page_num
    )

    return render(request, 'books/reader.html', {
        'book': book,
        'current_page': page_content,
        'page_num': page_num,
        'total_pages': total_pages,
    })


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if not book.is_available:
        messages.error(request, 'Книга уже выдана')
        return redirect('book_detail', book_id=book_id)

    # Простая логика выдачи
    book.is_available = False
    book.save()

    messages.success(request, f'Книга "{book.title}" выдана вам!')
    return redirect('book_detail', book_id=book_id)