from django.http.response import JsonResponse
from django.shortcuts import render
import io
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer
from .serializers import EmployeeSerializer
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


@csrf_exempt
def employee_create(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        python_data = JSONParser().parse(stream)
        serializer = EmployeeSerializer(data=python_data)
        if serializer.is_valid():
            serializer.save()
            res = {'msg': 'Data Created'}
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type='applicatin/json')
        # also we can use one line code for these two lines by jasonresponse
        # json_data = JSONRenderer().render(serializer.errors)
        # return HttpResponse(json_data, content_type='applicatin/json')
        return JsonResponse(json_data, Self=false)
