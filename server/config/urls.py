"""
URL configuration for SupplyChainIQ project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/forecasting/', include('apps.forecasting.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
