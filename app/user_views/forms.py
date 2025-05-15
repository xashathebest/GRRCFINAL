from django import forms # type: ignore
from .models import Article, User, Research
from django.contrib.auth.hashers import make_password # type: ignore
from PIL import Image
from .models import * # Models

class ResearchCategoryForm(forms.ModelForm):
    class Meta:
        model = ResearchCategory
        fields = ['name']
        

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
    category = forms.ModelChoiceField(
        queryset=ResearchCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 shadow-sm',
            'placeholder': 'Select a category...',
        })
    )

    class Meta:
        model = Research
        fields = ['title', 'content', 'category', 'image', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 shadow-sm',
                'placeholder': 'Enter research title...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 shadow-sm min-h-[150px]',
                'placeholder': 'Describe your research in detail...',
                'rows': 5,
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'accept': 'image/*',
                'id': 'image-upload',
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'accept': '.pdf',
                'id': 'pdf-upload',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(ResearchForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['pdf_file'].required = True
        self.fields['image'].required = False
        # Order categories alphabetically
        self.fields['category'].queryset = ResearchCategory.objects.all().order_by('name')
        
        # Add empty label for better UX
        self.fields['category'].empty_label = "Select a category (optional)"
        
        # If you want to style the select dropdown arrow
        self.fields['category'].widget.attrs.update({
            'class': self.fields['category'].widget.attrs['class'] + ' appearance-none bg-white bg-[url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpolyline points=\'6 9 12 15 18 9\'%3E%3C/polyline%3E%3C/svg%3E")] bg-no-repeat bg-[length:20px_20px] bg-[right_0.5rem_center] pr-10'
        })

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            if pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('PDF file size must not exceed 10MB.')
        return pdf_file

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:   
            return image  
        if image.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError("Image file too large ( > 5MB )")
        return image

class HeroSectionForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = [
            'title_line_1',
            'title_line_2',
            'description',
            'visit_us_link',
            'logo_image',
            'background_image',
            'learn_more_url',
        ]
        widgets = {
            'title_line_1': forms.TextInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'title_line_2': forms.TextInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-32',
                'rows': 4,
            }),
            'visit_us_link': forms.URLInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'logo_image': forms.ClearableFileInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'background_image': forms.ClearableFileInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
        }

class KeyObjectivesForm(forms.ModelForm):
    class Meta:
        model = KeyObjectives
        fields = '__all__'


class BannerImageForm(forms.ModelForm):
    class Meta:
        model = DynamicBannerImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'accept': 'image/*'
            }),
        }


class ContentCardForm(forms.ModelForm):
    class Meta:
        model = ContentCard
        fields = ['title', 'description', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-32',
                'rows': 4,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full p-2 mb-4 rounded border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'min': '1',
            }),
        }
        help_texts = {
            'order': 'Enter a number to determine the display order. Lower numbers appear first.'
        }
        
    def clean_order(self):
        order = self.cleaned_data.get('order')
        if order is not None and order < 1:
            raise forms.ValidationError("Order must be a positive number greater than 0.")
        return order


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'role', 'profile_image', 'linkedin_url', 'email']



class UGAHeroForm(forms.ModelForm):
    class Meta:
        model = UGAHeroSection
        fields = '__all__'

class UGAOverviewForm(forms.ModelForm):
    class Meta:
        model = UGAOverviewSection
        fields = '__all__'

class UGAOverviewCardForm(forms.ModelForm):
    class Meta:
        model = UGAOverviewCard
        fields = '__all__'

class UGAKeyAreaForm(forms.ModelForm):
    class Meta:
        model = UGAKeyArea
        fields = '__all__'

class ImplementationStepForm(forms.ModelForm):
    class Meta:
        model = UGAImplementationStep
        fields = '__all__'

class UGACallToActionForm(forms.ModelForm):
    class Meta:
        model = UGACallToAction
        fields = '__all__'

class ThemeSettingsForm(forms.ModelForm):
    class Meta:
        model = ThemeSettings
        fields = [
            'name', 'theme', 'is_active',
            'primary_color', 'secondary_color',
            'button_color', 'button_hover_color',
            'text_color', 'background_color',
            'nav_background', 'nav_text_color', 'nav_hover_color',
            'success_color', 'warning_color', 'error_color'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'placeholder': 'Theme Name'
            }),
            'theme': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-violet-600 focus:ring-violet-500 border-gray-300 rounded'
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'secondary_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'button_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'button_hover_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'text_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'background_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'nav_background': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'nav_text_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'nav_hover_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'success_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'warning_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
            'error_color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500',
                'type': 'color'
            }),
        }