def user_loans_info(request):
    if request.user.is_authenticated:
        from .models import Loan
        user_active_loans = Loan.objects.filter(user=request.user, status='active').values_list('book_id', flat=True)
        return {
            'user_active_loan_ids': list(user_active_loans)
        }
    return {'user_active_loan_ids': []}