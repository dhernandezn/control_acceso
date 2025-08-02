from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'), #ruta inicial
    path('consultar-rut/',views.consultar_rut, name='consultar_rut') #API consulta
]