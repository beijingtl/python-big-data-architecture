from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'counter', views.CounterViewSet)

urlpatterns = [
    path('', views.index),
    path('hi', views.hi),
    path('api/v1/', include(router.urls)),
    path('error/', views.error),
]