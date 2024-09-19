# inaEthe/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from django.http import HttpResponse, HttpResponseForbidden, FileResponse, Http404, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Q
from django.shortcuts import render
from inaEthe.models import Content, Book
from users.models import CustomUser
from django.conf import settings
from django.utils.timezone import now, timedelta
from django.utils import timezone
from django.urls import reverse_lazy

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.db.models import Count
from django.views.decorators.http import require_POST

def welcome(request):
    return render(request, 'inaEthe/welcome.html')

@login_required
def index(request):
    contents = Content.objects.all().order_by('-created_at')  # Order by latest first
    following_ids = request.user.following.values_list('id', flat=True) if request.user.is_authenticated else []
    return render(request, 'inaEthe/index.html', {'contents': contents, 'following_ids': following_ids})

@login_required  # Ensure only logged-in users can create content
def create_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            new_category_name = form.cleaned_data.get('new_category')

            if new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
            else:
                category = form.cleaned_data.get('category')

            # Create the content but don't save it to the database yet
            content = form.save(commit=False)
            content.category = category
            content.author = request.user  # Set the current logged-in user as the author

            # Now save the content to the database
            content.save()
            return redirect('inaEthe:index')  # Replace with your desired redirect URL
    else:
        form = ContentForm()
    return render(request, 'inaEthe/create_content.html', {'form': form})

def content_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    contents = Content.objects.filter(category=category)
    return render(request, 'inaEthe/content_by_category.html', {'category': category, 'contents': contents})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    contents = category.contents.all()  # Use the related name here
    return render(request, 'inaEthe/category_detail.html', {'category': category, 'contents': contents})

@login_required
def content_list(request):
    published_content = Content.objects.filter(author=request.user, status='published')
    return render(request, 'inaEthe/content_list.html', {'published_content': published_content})

@login_required
def edit_content(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content updated successfully!')
            return redirect('inaEthe:content_detail', pk=content.pk)
    else:
        form = ContentForm(instance=content)
    return render(request, 'inaEthe/edit_content.html', {'form': form})

@login_required
def delete_content(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted successfully!')
        return redirect('inaEthe:content_list')
    return render(request, 'inaEthe/delete_content.html', {'content': content})

@login_required
def content_list(request):
    contents = Content.objects.filter(author=request.user)
    return render(request, 'inaEthe/content_list.html', {'contents': contents})

@login_required
def content_detail(request, pk):
    content = get_object_or_404(Content, pk=pk)
    return render(request, 'inaEthe/content_detail.html', {'content': content})

@login_required
def content_update(request, pk):
    content = get_object_or_404(Content, pk=pk)

    if request.user != content.author:
        return HttpResponseForbidden("You are not allowed to edit this content.")

    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect('inaEthe:content-detail', pk=content.pk)
    else:
        form = ContentForm(instance=content)

    return render(request, 'inaEthe/content_update.html', {'form': form})

@login_required
def like_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.user in content.likes.all():
        content.likes.remove(request.user)
        liked = False
    else:
        content.likes.add(request.user)
        liked = True

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def manage_permissions(request):
    user_content = Content.objects.filter(author=request.user)
    
    if request.method == 'POST':
        content_id = request.POST.get('content_id')
        permission = request.POST.get('permission') == 'on'
        content = get_object_or_404(Content, id=content_id, author=request.user)
        content.permission_granted = permission
        content.save()
        return redirect('inaEthe:manage_permissions')
    return render(request, 'inaEthe/manage_permissions.html', {'user_content': user_content})

@login_required
def other_books(request):
    user_content = request.user.content_set.all()  # Get all content from the user
    books = Book.objects.exclude(content__in=user_content)  # Exclude books that contain the user's content
    return render(request, 'inaEthe/other_books.html', {'books': books})

def submit_content(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        category_id = request.POST.get('category')
        category = get_object_or_404(Category, id=category_id)
        content = Content(user=request.user, title=title, body=body, category=category, permission_granted=True)
        content.save()
        return redirect('users:profile')
    categories = Category.objects.all()
    return render(request, 'inaEthe/submit_content.html', {'categories': categories})

def compile_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    contents = book.contents.all()
    return render(request, 'inaEthe/book_detail.html', {'book': book, 'contents': contents})

def generate_pdf(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    contents = book.content.all()  # Correct attribute name
    
    # Generate PDF logic
    context = {'book': book, 'contents': contents}
    html_string = render_to_string('inaEthe/pdf_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=book_{book_id}.pdf'
    result = BytesIO()
    pdf = pisa.CreatePDF(html_string, dest=result)
    response.write(result.getvalue())
    return response

@login_required
def book_detail(request, id):
    book = Book.objects.get(id=id)
    return render(request, 'inaEthe/book_detail.html', {'book': book})

@login_required
def user_books(request):
    user_contents = Content.objects.filter(author=request.user)
    books_with_user_content = Book.objects.filter(content__in=user_contents).distinct()
    return render(request, 'inaEthe/user_books.html', {'books': books_with_user_content})

def explore(request):
    # Annotate the number of likes for each content and order by this count
    trending_content = Content.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')[:5]
    recommended_content = get_recommended_content(request.user)
    categories = Category.objects.all()

    return render(request, 'inaEthe/explore.html', {
        'trending_content': trending_content,
        'recommended_content': recommended_content,
        'categories': categories,
    })

def get_recommended_content(user):
    if hasattr(user, 'preferred_categories') and user.preferred_categories.exists():
        # If the user has preferred categories, filter content by those categories
        return Content.objects.filter(category__in=user.preferred_categories.all()).order_by('-created_at')[:5]
    else:
        # If no preferred categories, return recently created content as a fallback
        return Content.objects.all().order_by('-created_at')[:5]

@staff_member_required
def approve_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    content.is_approved_for_book = True
    content.save()
    messages.success(request, 'Content approved for compilation!')
    return redirect('inaEthe:content_list')

@staff_member_required
def unapprove_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    content.is_approved_for_book = False
    content.save()
    messages.success(request, 'Content removed from compilation approval!')
    return redirect('inaEthe:content_list')

def book_list(request):
    books = Book.objects.all()
    return render(request, 'inaEthe/book_list.html', {'books': books})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    has_purchased = Purchase.objects.filter(user=request.user, book=book).exists()
    return render(request, 'inaEthe/book_detail.html', {'book': book, 'has_purchased': has_purchased})

def book_preview(request, book_id):
    #book = get_object_or_404(Book, id=book_id, is_published=True)
    book = get_object_or_404(Book, id=book_id, published_date__isnull=False)

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            # Handle the purchase process
            return redirect('inaEthe:book_download', book_id=book.id)

    else:
        form = PurchaseForm()
    return render(request, 'inaEthe/book_preview.html', {
        'book': book,
        'form': form,
    })
    
@login_required
def purchase_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if Purchase.objects.filter(user=request.user, book=book).exists():
        return HttpResponse("You already purchased this book.")
    Purchase.objects.create(user=request.user, book=book)
    return redirect('inaEthe:book_download', book_id=book.id)

@login_required
def book_download(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if the user has purchased this book
    purchase = Purchase.objects.filter(user=request.user, book=book).first()
    if not purchase:
        return redirect('inaEthe:purchase_book', book_id=book.id)

    # Serve the PDF for download
    response = HttpResponse(book.pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'

    # Mark as downloaded if not already
    if not purchase.is_downloaded:
        purchase.is_downloaded = True
        purchase.save()
    return response

def search_results(request):
    query = request.GET.get('q')
    
    if query:
        # Search in Content model based on title, body, or author's username
        content_results = Content.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query) | Q(author__username__icontains=query)
        )
        book_results = Book.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        user_results = CustomUser.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
        category_results = Category.objects.filter(
            Q(name__icontains=query)
        )
    else:
        content_results = Content.objects.none()
        book_results = Book.objects.none()
        user_results = CustomUser.objects.none()
        category_results = Category.objects.none()
    
    context = {
        'content_results': content_results,
        'book_results': book_results,
        'user_results': user_results,
        'category_results': category_results,
        'query': query,
    }
    return render(request, 'inaEthe/search_results.html', context)

