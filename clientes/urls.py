from django.urls import path
from .views import ValidarRutView

urlpatterns = [
    path('validar-rut/', ValidarRutView.as_view(),name='validar_rut'),
]