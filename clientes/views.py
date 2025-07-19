from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import re

# Create your views here.
class ValidarRutView(APIView):
    def post(self, request):
        rut = request.data.get('rut','')
        valido = self.validar_rut(rut)
        mensaje = "RUT válido" if valido else "RUT inválido"
        return Response({
            "rut": rut,
            "valido": valido,
            "mensaje": mensaje
        }, status=status.HTTP_200_OK)
    
    def validar_rut(self,rut):
        rut = rut.replace(".", "").replace("-", "")
        if len(rut) < 2:
            return False
        cuerpo, dv = rut[:-1], rut[-1].upper()
        try:
            suma = 0
            multiplo = 2
            for c in reversed(cuerpo):
                suma += int(c) * multiplo
                multiplo = 2 if multiplo == 7 else multiplo + 1
            dvr = 11 - (suma % 11)
            if dvr == 11:
                dvr = '0'
            elif dvr == 10:
                dvr = 'K'
            else:
                dvr = str(dvr)
            return dvr == dv
        except:
            return False