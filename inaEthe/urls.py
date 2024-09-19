from django.urls import path
from . import views

app_name = 'inaEthe'

urlpatterns = [
    #path('', views.welcome, name='welcome'),
    path('', views.index, name='index'),
    
    path('create-content/', views.create_content, name='create_content'),
    path('category/<int:category_id>/', views.content_by_category, name='content_by_category'),
    path('category/detail/<int:pk>/', views.category_detail, name='category_detail'),
    #path('content_detail/<int:pk>/', views.content_detail, name='content_detail'),
    path('content/<int:pk>/', views.content_detail, name='content_detail'),
    path('edit-content/<int:pk>/', views.edit_content, name='edit_content'),
    path('delete-content/<int:pk>/', views.delete_content, name='delete_content'),
    path('content-list/', views.content_list, name='content_list'),
    path('approve-content/<int:pk>/', views.approve_content, name='approve_content'),
    path('unapprove-content/<int:pk>/', views.unapprove_content, name='unapprove_content'),
    path('like/<int:content_id>/', views.like_content, name='like_content'),
    path('generate-pdf/<int:book_id>/', views.generate_pdf, name='generate_pdf'),
    path('explore/', views.explore, name='explore'),
    
    path('submit-content/', views.submit_content, name='submit_content'),
    path('generate-pdf/<int:book_id>/', views.generate_pdf, name='generate_pdf'),

    #path('compile_book/', views.compile_content_to_book, name='compile_Content_to_book'),
    path('your-books/', views.user_books, name='user_books'),
    
    path('book-list/', views.book_list, name='book_list'),
    path('book-detail<int:book_id>/', views.book_detail, name='book_detail'),
    path('book-preview/<int:book_id>/', views.book_preview, name='book_preview'),
    path('book-download/<int:book_id>/', views.book_download, name='book_download'),
    path('purchase-book/<int:book_id>/', views.purchase_book, name='purchase_book'),
    path('other-books/', views.other_books, name='other_books'),
    
    path('compile-book/<int:book_id>/', views.compile_book, name='compile_book'),
    path('search/', views.search_results, name='search_results'),
]

