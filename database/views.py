from django.http import HttpResponse, StreamingHttpResponse, JsonResponse, FileResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from database.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from mrnadesign_api import settings
import os
from . import utils
from io import BytesIO
import ast
from django.db.models import Count
import json
import pandas as pd
import random

@api_view(["GET"])
def download_protein_cif(request):
    querydict = request.query_params.dict()
    sequence = querydict['sequence'][:-1]
    content = utils.esm_fold_cif_api(sequence)
    
    content_bytes = content.encode('utf-8')
    buffer = BytesIO(content_bytes)
    response = response = FileResponse(buffer)
    response['Content-Disposition'] = 'attachment; filename="protein.cif"'
    response['Content-Type'] = 'text/plain'

    return response