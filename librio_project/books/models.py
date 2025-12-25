from django.db import models
import os


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name


class Book(models.Model):
    ACCESS_LEVELS = [
        ('free', 'Свободный'),
        ('limited', 'Ограниченный'),
        ('premium', 'Премиум'),
    ]

    title = models.CharField(max_length=500)
    is_available = models.BooleanField(default=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='free')
    max_loan_days = models.IntegerField(default=14)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)



    def save(self, *args, **kwargs):
        self.is_available = True
        super().save(*args, **kwargs)
class BookContent(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='content')
    text = models.TextField()  # Полный текст книги
    is_public = models.BooleanField(default=False)  # Бесплатный доступ?

    def split_into_pages(self, chars_per_page=2000):
        text = self.text
        pages = []
        for i in range(0, len(text), chars_per_page):
            pages.append(text[i:i + chars_per_page])
        return pages
    def __str__(self):
        return self.title


class BookReadingLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page = models.IntegerField(default=1)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-read_at']

    def __str__(self):
        return f"{self.user.username} читал {self.book.title} (стр. {self.page})"

