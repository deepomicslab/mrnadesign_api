from analysis.views import *
from rest_framework.routers import DefaultRouter
from django.urls import include, re_path, path

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('files/<path:path>/', viewresultfile, name='viewresultfile'),
]