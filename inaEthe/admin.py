from django.contrib import admin
from .models import *

class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_approved_for_book')
    list_filter = ('is_approved_for_book', 'author')
    search_fields = ('title', 'body')
    actions = ['approve_for_book', 'unapprove_for_book', 'add_to_book']

    def approve_for_book(self, request, queryset):
        queryset.update(is_approved_for_book=True)
        self.message_user(request, "Selected content has been approved for compilation.")

    def unapprove_for_book(self, request, queryset):
        queryset.update(is_approved_for_book=False)
        self.message_user(request, "Selected content has been removed from approval for compilation.")

    approve_for_book.short_description = "Approve selected content for compilation"
    unapprove_for_book.short_description = "Unapprove selected content for compilation"

    def add_to_book(self, request, queryset):
        selected_content = queryset.filter(permission_granted=True)
        # Assuming there is a specific book in progress, otherwise let the admin select
        book = Book.objects.get(title="Current Compilation Book")
        for content in selected_content:
            book.content.add(content)
        self.message_user(request, f"{selected_content.count()} items were added to the book.")
    add_to_book.short_description = "Add selected content to the book"

admin.site.register(Content, ContentAdmin)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Purchase)

