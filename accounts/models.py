from django.contrib.auth.models import User
from django.db import models

class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.user.get_full_name() or self.user.username

class Organization(models.Model):
    STATUS = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    name = models.CharField(max_length=150)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=250)
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    coordinators = models.ManyToManyField(User, related_name='coordinated_organizations', blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
