from django.contrib import admin
from .models import Cause, Certificate, HourLog, Milestone, Opportunity, Review, Signup
for model in [Cause, Certificate, HourLog, Milestone, Opportunity, Review, Signup]:
    admin.site.register(model)
