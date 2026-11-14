from django.urls import path
from . import views
urlpatterns = [path('', views.report, name='report'), path('hours.csv', views.export_csv, name='export-csv'), path('service.pdf', views.pdf_report, name='pdf-report')]
