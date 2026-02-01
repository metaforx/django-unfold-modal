from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from .models import Author, Book, Category, Chapter, Profile, Publisher, Tag


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ["author", "bio"]
    autocomplete_fields = ["author"]


@admin.register(Publisher)
class PublisherAdmin(ModelAdmin):
    list_display = ["name", "address"]
    search_fields = ["name"]


class ChapterInline(TabularInline):
    """Inline for testing related fields within inline forms."""

    model = Chapter
    extra = 1
    fields = ["number", "title", "editor"]
    autocomplete_fields = ["editor"]


@admin.register(Book)
class BookAdmin(ModelAdmin):
    """
    Main admin demonstrating all related-object widget configurations:
    - category: normal ForeignKey select
    - tags: ManyToMany filter_horizontal
    - author: autocomplete_fields (Select2)
    - publisher: raw_id_fields (lookup popup)
    - chapters: inline with related field (editor)
    """

    list_display = ["title", "category", "author", "publisher"]
    list_filter = ["category", "tags"]
    search_fields = ["title"]

    # Different widget configurations for related fields
    autocomplete_fields = ["author"]
    raw_id_fields = ["publisher"]
    filter_horizontal = ["tags"]

    fieldsets = [
        (None, {"fields": ["title"]}),
        ("Classification", {"fields": ["category", "tags"]}),
        ("People", {"fields": ["author", "publisher"]}),
    ]

    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(ModelAdmin):
    list_display = ["book", "number", "title", "editor"]
    list_filter = ["book"]
    autocomplete_fields = ["book", "editor"]
