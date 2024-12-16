from database.views import *
from rest_framework.routers import DefaultRouter
from django.urls import include, re_path, path

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^download_protein_cif/$', download_protein_cif, name='download_protein_cif'),

]