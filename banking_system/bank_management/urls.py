from django.urls import path
from bank_management.views import *

urlpatterns = [
    path("",index,name="index")
]