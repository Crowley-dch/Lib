from loans.models import Loan


def check_book_access(book, user):

    if not hasattr(book, 'content'):
        return False

    if book.content.is_public:
        return True

    if not user.is_authenticated:
        return False

    has_active_loan = Loan.objects.filter(
        book=book,
        user=user,
        status='active'
    ).exists()

    if has_active_loan:
        return True

    try:
        user_type = user.userprofile.user_type
        if user_type in ['admin', 'librarian']:
            return True
    except:
        pass

    return False


def split_text_into_pages(text, chars_per_page=2000):
    if not text:
        return []

    pages = []
    for i in range(0, len(text), chars_per_page):
        pages.append(text[i:i + chars_per_page])

    return pages


def add_watermark(text, user_id, book_id, page_num):

    watermark = f'<!-- Librio: user={user_id}, book={book_id}, page={page_num} -->'
    return text + '\n' + watermark