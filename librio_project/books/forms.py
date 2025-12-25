from django import forms
from .models import Book, Author, Genre

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'access_level', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название',
            'author': 'Автор',
            'genre': 'Жанр',
            'access_level': 'Уровень доступа',
            'description': 'Описание'
        }
