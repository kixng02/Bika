# forms.py
from django import forms
from .models import User
from .models import Announcements,Claims, Ticket

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profilePicture', 'firstname','lastname', 'email', 'address','contactNumber','city','nationalId','securityQuestion']  
        # Add any other fields you want to update

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Announcements
        fields = ['title', 'content']
        labels = {
            'title': '',  # Empty label to remove it
            'content': '',  # Empty label to remove it
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Content','rows': 6}),
        }

class ClaimForm(forms.Form):
    CLAIM_CHOICES = [ ('1', 'Damage to property'),('2', 'Damage to crops'),('3', 'Damage to livestock'),('4', 'Human injury')]
    
    claim = forms.ChoiceField(choices=CLAIM_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    claim_image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}), required=False)
    details = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True)

    class Meta:
        model = Claims  # Specify the model
        fields = ['claim', 'claim_image', 'details']  # Specify the fields from the model to include in the form

    def save(self, request, commit=True):
        claim = super().save(commit=False)  # Get the instance of the claim without saving to the database yet
        claim.user = request.user  # Set the user to the currently logged-in user
        if commit:
            claim.save()  # Save the claim to the database
        return claim
    

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'question_description']

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'question_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

        }


class AdminClaimForm(forms.ModelForm):
    CLAIM_CHOICES = [
        ('Damage to property', 'Damage to property'),
        ('Damage to crops', 'Damage to crops'),
        ('Damage to livestock', 'Damage to livestock'),
        ('Human injury', 'Human injury'),
    ]
    STATUS_CHOICES = [
        ('', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    claims = forms.ChoiceField(choices=CLAIM_CHOICES, widget=forms.Select(attrs={'class': 'field-input'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'field-input'}), required=False)

    class Meta:
        model = Claims
        fields = ['user', 'claims', 'details', 'status', 'claim_image']
        widgets = {
            'user':        forms.Select(attrs={'class': 'field-input'}),
            'details':     forms.Textarea(attrs={'class': 'field-input', 'rows': 3}),
            'claim_image': forms.ClearableFileInput(attrs={'class': 'field-input'}),
        }


class AdminTicketForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('assigned', 'Assigned'),
        ('fixed',    'Resolved'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'field-input'}),
    )

    class Meta:
        model = Ticket
        fields = ['status', 'response']
        widgets = {
            'response': forms.Textarea(attrs={'class': 'field-input', 'rows': 4}),
        }