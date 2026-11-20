from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [path('', include('accounts.urls')), path('admin/', admin.site.urls), path('', include('core.urls')), path('reports/', include('reports.urls')),
               path('credits/', TemplateView.as_view(template_name='credits.html'), name='credits')]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
