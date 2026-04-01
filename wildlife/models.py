from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # Add additional fields here
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    nationalId = models.CharField(max_length=100, blank=True)
    contactNumber = models.CharField(max_length=20, blank=True, null=True)
    profilePicture = models.ImageField(upload_to="images/", default="images/placeholder_img.jpg")
    securityQuestion = models.TextField(max_length=500, blank=True)
    status = models.BooleanField(default=False)

    def clean(self):
        # Custom validation and formatting logic
        if self.contactNumber:
            # Normalize the phone number by removing non-numeric characters
            self.contactNumber = ''.join(filter(str.isdigit, self.contactNumber))


class Announcements(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    subject = models.CharField(max_length=100)
    question_description = models.TextField()  # Use TextField for longer descriptions
    status = models.CharField(max_length=100)
    response = models.TextField()  # Use TextField for longer responses
    support_officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tickets', null=True) #null=true enable saving even if support officer has not been assigned
    submission_timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tickets')

class Claims(models.Model):
    details = models.CharField(max_length=100)
    claims = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    claim_image = models.ImageField(upload_to='images/', default="images/placeholder_img.jpg")
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Add this line
    STATUS_CHOICES = (
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f'Claim #{self.id} - {self.user.username} - {self.status}'