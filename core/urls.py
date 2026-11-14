from django.urls import path
from . import views
urlpatterns = [
    path('opportunities/', views.opportunity_list, name='opportunity-list'),
    path('opportunities/search/', views.opportunity_search, name='opportunity-search'),
    path('opportunities/new/', views.opportunity_create, name='opportunity-create'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity-detail'),
    path('opportunities/<int:pk>/edit/', views.opportunity_edit, name='opportunity-edit'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity-delete'),
    path('opportunities/<int:pk>/apply/', views.apply, name='apply'),
    path('opportunities/<int:pk>/signups/', views.manage_signups, name='manage-signups'),
    path('signups/<int:signup_id>/hours/', views.submit_hours, name='submit-hours'),
    path('hours/<int:log_id>/verify/', views.verify_hours, name='verify-hours'),
    path('opportunities/<int:pk>/review/', views.review, name='review'),
    path('certificates/', views.certificates, name='certificates'),
    path('certificates/<uuid:certificate_id>/', views.certificate_verify, name='certificate-verify'),
    path('certificates/<uuid:certificate_id>/download/', views.certificate_pdf, name='certificate-pdf'),
]
