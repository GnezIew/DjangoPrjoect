from django.urls import path
from BackstageApp.views import *
urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('base/',base),
    path('register_store/',register_store),
    path('add_goods/',add_goods),
    path('list_goods/',list_goods)
]