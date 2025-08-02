from django.urls import path, include
from .views import ValidarRutView

urlpatterns = [
    path('validar-rut/', ValidarRutView.as_view(),name='validar_rut'),
    path('', include('frontend.urls')),
]