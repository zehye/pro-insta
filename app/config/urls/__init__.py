from django.urls import path, include

urlpatterns = [
    path('api/', include('config.urls.apis')),
    path('', include('config.urls.views')),
]
