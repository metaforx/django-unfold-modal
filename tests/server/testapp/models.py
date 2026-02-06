from django.db import models


class Category(models.Model):
    """Simple model for ForeignKey select widget testing."""

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Simple model for ManyToMany select widget testing."""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    """Model for autocomplete_fields and OneToOne testing."""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """Model for raw_id_fields lookup widget testing."""

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Main model demonstrating various related-object widget types:
    - category: ForeignKey (normal select)
    - tags: ManyToMany (multiple select)
    - author: ForeignKey (autocomplete_fields)
    - publisher: ForeignKey (raw_id_fields)
    """

    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.title


class Chapter(models.Model):
    """
    Inline model for testing related fields within inline forms.
    - editor: ForeignKey to Author (related field inside inline)
    """

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=200)
    number = models.PositiveIntegerField()
    editor = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_chapters",
    )

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Chapter {self.number}: {self.title}"


class Country(models.Model):
    """
    Level C in nested chain: Country -> City -> Venue.
    Used to test nested modal scenarios (creating Venue can open City modal,
    which can open Country modal).
    """

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    """
    Level B in nested chain: Country -> City -> Venue.
    Has FK to Country, so add/change links can trigger modal.
    """

    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Venue(models.Model):
    """
    Level A in nested chain: Country -> City -> Venue.
    Has FK to City, which has FK to Country.
    Creating a Venue can open modal for City, which can open modal for Country.
    """

    name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="venues")
    address = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Long-form model with many fields to force iframe scrolling.
    Tests modal behavior with large forms.
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.ForeignKey(
        Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name="events"
    )
    organizer = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="organized_events"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    capacity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_public = models.BooleanField(default=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return self.title
