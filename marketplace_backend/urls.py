from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authApis/', include('authentication.urls')),
    path('logisticsDeliveryApis/', include('logistics_delivery.urls')),
    path('ordersApis/', include('orders.urls')),
    path('paymentApis/', include('payment.urls')),
    path('listingsApis/', include('product_listings.urls')),
    path('profileApis/', include('profile_management.urls')),
    path('searchFiltersApis/', include('search_filters.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
