from django.shortcuts import render
from rest_framework import viewsets
from . import models
from . import serializers

class DepartmentViewset(viewsets.ModelViewSet):
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer