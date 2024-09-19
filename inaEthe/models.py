# inaEthe/models.py
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Content(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved_for_book = models.BooleanField(default=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_content', blank=True)
    # Add the ForeignKey to Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='contents', blank=True, null=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.ManyToManyField(Content, related_name='books')
    cover_image = models.ImageField(upload_to='book_covers/')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    published_date = models.DateField()
    pdf_file = models.FileField(upload_to='books/', null=True, blank=True)  # Compiled book file
    preview_text = models.TextField(blank=True, null=True)  # Preview text of the book
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='books', default=1)  # Link to the user

    def __str__(self):
        return self.title

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_downloaded = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} purchased {self.book.title}'