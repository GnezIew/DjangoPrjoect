from django.urls import path
from BackstageApp.views import *
urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index)
]