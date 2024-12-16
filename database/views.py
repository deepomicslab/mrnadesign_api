from django.http import FileResponse
from database.serializers import *
from rest_framework.decorators import api_view
from . import utils
from io import BytesIO
from mrnadesign_api import settings_local as local_settings

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

@api_view(['GET'])
def downloadbypaath(request, path):
    file_path = local_settings.MRNADESIGN_DATABASE + path
    file = open(file_path, 'rb')
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'text/plain'
    return response