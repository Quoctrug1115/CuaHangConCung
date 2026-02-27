from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gis_utils.urls')),
    path('accounts/', include('accounts.urls')),
    path('cua-hang/', include('stores.urls')),
    path('san-pham/', include('products.urls')),
    path('don-hang/', include('orders.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
