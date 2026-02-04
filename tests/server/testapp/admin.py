from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Author,
    Book,
    Category,
    Chapter,
    City,
    Country,
    Event,
    Profile,
    Publisher,
    Tag,
    Venue,
)


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


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    """
    Level C admin for nested modal testing.
    Needs search_fields for potential autocomplete usage.
    """

    list_display = ["name"]
    search_fields = ["name"]


@admin.register(City)
class CityAdmin(ModelAdmin):
    """
    Level B admin for nested modal testing.
    FK to Country uses normal select (has add link to trigger modal).
    """

    list_display = ["name", "country"]
    search_fields = ["name"]
    list_filter = ["country"]
    # country is normal FK select (not autocomplete) to expose add/change links


@admin.register(Venue)
class VenueAdmin(ModelAdmin):
    """
    Level A admin for nested modal testing.
    FK to City uses normal select (has add link).
    Creating Venue -> modal for City -> nested modal for Country.
    """

    list_display = ["name", "city", "address"]
    search_fields = ["name", "address"]
    list_filter = ["city__country"]
    # city is normal FK select (not autocomplete) to expose add/change links


@admin.register(Event)
class EventAdmin(ModelAdmin):
    """
    Long-form admin to exercise iframe scrolling.
    Many fields organized in fieldsets.
    """

    list_display = ["title", "date", "start_time", "venue", "organizer", "is_public"]
    list_filter = ["is_public", "category", "date"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["organizer"]

    fieldsets = [
        (
            "Basic Information",
            {
                "fields": ["title", "description", "category"]
            },
        ),
        (
            "Schedule",
            {
                "fields": ["date", "start_time", "end_time"]
            },
        ),
        (
            "Location & Organization",
            {
                "fields": ["venue", "organizer"]
            },
        ),
        (
            "Details",
            {
                "fields": ["capacity", "price", "is_public", "website"]
            },
        ),
        (
            "Additional Notes",
            {
                "fields": ["notes"],
                "classes": ["collapse"],
            },
        ),
    ]
