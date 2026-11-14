import uuid
from django.contrib.auth.models import User
from django.db import models
from accounts.models import Organization

class Cause(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name

class Opportunity(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=160)
    description = models.TextField()
    causes = models.ManyToManyField(Cause, blank=True, related_name='opportunities')
    location = models.CharField(max_length=180)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=10)
    requirements = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title
    @property
    def confirmed_count(self): return self.signups.filter(status='confirmed').count()
    @property
    def available_slots(self): return max(self.capacity - self.confirmed_count, 0)

class Signup(models.Model):
    STATUS = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected'), ('completed', 'Completed')]
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signups')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='signups')
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['volunteer', 'opportunity'], name='unique_volunteer_opportunity')]

class HourLog(models.Model):
    STATUS = [('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')]
    signup = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name='hour_logs')
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    verified_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_hours')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

class Milestone(models.Model):
    name = models.CharField(max_length=80)
    required_hours = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f'{self.name} ({self.required_hours} hours)'

class Certificate(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['volunteer', 'milestone'], name='unique_volunteer_milestone')]

class Review(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['volunteer', 'opportunity'], name='unique_volunteer_review')]
