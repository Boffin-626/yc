# inaEthe/forms.py
from django import forms
from .models import Content, Book

class ContentForm(forms.ModelForm):
    new_category = forms.CharField(required=False, label='New Category', max_length=100)

    class Meta:
        model = Content
        fields = ['title', 'body', 'category']  # Ensure 'category' is in the fields list

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')

        if not category and not new_category:
            raise forms.ValidationError('Please select an existing category or add a new one.')

        return cleaned_data

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'cover_image', 'price', 'published_date']
        
class CompileBookForm(forms.ModelForm):
    content = forms.ModelMultipleChoiceField(
        queryset=Content.objects.none(), 
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select content to include in the book"
    )

    class Meta:
        model = Book
        fields = ['title', 'description', 'cover_image', 'price', 'content']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['content'].queryset = Content.objects.filter(author=user)

class PurchaseForm(forms.Form):
    confirm_purchase = forms.BooleanField(required=True, label="Confirm Purchase")