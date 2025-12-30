from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Extends the default User model to add e-commerce specific fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    
    # For email verification (Phase 4 readiness)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signals to automatically create a Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class EmailLog(models.Model):
    """
    Tracks every email sent by the system for auditing and debugging.
    """
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )

    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField() # Store the HTML or Text content
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} -> {self.recipient} ({self.status})"