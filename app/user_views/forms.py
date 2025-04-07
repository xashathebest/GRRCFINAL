from django import forms # type: ignore
from .models import Article, User, Research
from django.contrib.auth.hashers import make_password # type: ignore
from PIL import Image
import io

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': 'Enter article title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 min-h-[200px]',
                'placeholder': 'Enter article content'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'accept': 'image/*'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        # Allow existing image to remain if no new image is uploaded
        if not image:  
            return image  

        # Check file size
        if image.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError("Image file too large ( > 5MB )")

        # Validate that the file is a real image
        try:
            img = Image.open(image)
            img.verify()  # Verifies if the file is a valid image
        except (IOError, SyntaxError):
            raise forms.ValidationError("File is not a valid image")

        return image

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long!")
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 100:
            raise forms.ValidationError("Content must be at least 100 characters long!")
        return content


from django import forms
from django.contrib.auth.hashers import make_password
from .models import User  # Ensure you import the User model

class UserForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Enter password'
        }),
        required=False,  # Change to False so it's optional when editing
        help_text='Password must be at least 8 characters long and contain at least one number.'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Confirm password'
        }),
        required=False  # Make confirm password optional
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'}))
    
    is_active = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email', 'role', 'password', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': 'Enter last name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'border p-2 rounded w-full', 
                'placeholder': 'Enter middle name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': 'Enter email address'
            }),
        }

    def clean_middle_name(self):
        """Ensure middle_name is optional and return an empty string if not provided."""
        return self.cleaned_data.get('middle_name', '') or ''

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")

        if password:
            if len(password) < 8:
                self.add_error('password', "Password must be at least 8 characters long!")
            if not any(char.isdigit() for char in password):
                self.add_error('password', "Password must contain at least one number!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # If editing and password is blank, keep the old password
        if not self.cleaned_data['password'] and self.instance.pk:
            user.password = User.objects.get(pk=self.instance.pk).password
        else:
            user.password = make_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class ResearchForm(forms.ModelForm):
    class Meta:
        model = Research
        fields = ['title', 'content', 'image', 'pdf_file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }
