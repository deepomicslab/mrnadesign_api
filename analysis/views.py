from django.http import FileResponse
from database.serializers import *
from rest_framework.decorators import api_view

@api_view(['GET'])
def viewresultfile(request, path):
    file = open('/'+path, 'rb') # 是一个绝对路径，home/platform/...., 在前面加上根目录的 “/” 
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'text/plain'
    response['Access-Control-Allow-Origin'] = 'https://www.ncbi.nlm.nih.gov' 
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response