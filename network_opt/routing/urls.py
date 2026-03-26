from django.urls import path, include
from rest_framework.routers import DefaultRouter

from routing.views import (
    NodeViewSet,
    EdgeViewSet,
    RouteView,
    RouteHistoryView,
)

router = DefaultRouter()
router.register(r'nodes', NodeViewSet, basename='node')
router.register(r'edges', EdgeViewSet, basename='edge')

urlpatterns = [
    path('', include(router.urls)),
    path('routes/shortest/', RouteView.as_view(), name='route-shortest'),
    path('routes/history/', RouteHistoryView.as_view(), name='route-history'),
]
