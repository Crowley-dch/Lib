from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from .models import UserProfile
from django.contrib.auth import logout

def home(request):
    return render(request, 'home.html')
def user_logout(request):
    logout(request)
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Создаем UserProfile с типом 'student' по умолчанию
            UserProfile.objects.create(
                user=user,
                user_type='student',  # Все новые пользователи - студенты
                phone=form.cleaned_data.get('phone')
            )

            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь можно войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('home')  # Создадим позже
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})