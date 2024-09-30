from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('billing.urls')),
    path('feedback/', include('your_app_name.urls')),  # replace 'your_app_name' with your app name
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)