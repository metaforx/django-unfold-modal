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


class Profile(models.Model):
    """OneToOne related model testing."""

    author = models.OneToOneField(Author, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.author.name}"


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
