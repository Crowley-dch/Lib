from django.contrib import admin
from .models import Genre, Author, Book
from django.utils.html import format_html

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name']
    search_fields = ['full_name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'genre', 'is_available', 'access_level','cover_preview']
    list_filter = ['is_available', 'access_level', 'genre']
    search_fields = ['title', 'author__full_name']
    readonly_fields = ('cover_preview',)
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.cover_image.url)
        return "Нет обложки"
    cover_preview.short_description = 'Превью обложки'