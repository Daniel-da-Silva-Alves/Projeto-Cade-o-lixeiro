from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracking.urls')),  # Ajuste aqui para que a URL raiz aponte para 'tracking.urls'
]

