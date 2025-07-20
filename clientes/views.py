from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Prohibidos, Seguimientos, Peps, Sospechosos, Autoexcluidos
from datetime import date
import re
import requests

# Create your views here.
class ValidarRutView(APIView):
    def post(self, request):
        rut = request.data.get('rut','')
        valido = self.validar_rut(rut)
        #mensaje = "RUT válido" 
        if not valido:
            return Response({
                "rut": rut,
                "valido": False,
                "mensaje": "Rut inválido",
                "prohibido": None
            },status=status.HTTP_200_OK)
        
        rut_limpio = rut.replace(".","").upper()

        #validar Prohibidos
        # prohibido = self.validar_prohibido(rut_limpio)
        # if prohibido:
        #     return prohibido
        #validar Seguimientos
        #validar PEP
        pep_resultado = self.validar_pep(rut_limpio)
        if pep_resultado.get("es_pep"):
            return Response({
                "rut": rut,
                "valido": True,
                "prohibido": True,
                "tipo": "pep",
                "nombre": pep_resultado["nombre"]
            }, status=status.HTTP_200_OK)
        elif "error" in pep_resultado:
            return Response({
                "rut": rut,
                "valido": True,
                "prohibido": False,
                "error": pep_resultado["error"]
            }, status=status.HTTP_502_BAD_GATEWAY)
        #validar Sospechosos

    def validar_prohibido(self, rut):

        cliente = Prohibidos.objects.filter(rut=rut).first()
        
        if cliente and cliente.fecha_inicio <= date.today() <= cliente.fecha_termino:
            return Response({
                "rut": rut,
                "valido": True,
                "tipo": "prohibido",
                "nombre": cliente.nombre,
                "desde": cliente.fecha_inicio,
                "hasta": cliente.fecha_termino,
            })

        return Response({
            "rut": rut,
            "valido": True,
            "prohibido": False,
            "mensaje": "RUT válido y sin prohibición"
        }, status=status.HTTP_200_OK)
    
    def validar_seguimiento(self, rut):
        cliente = Seguimientos.objects.filter(rut=rut).first()
        if cliente:
            return Response({
                "rut": rut,
                "valido": True,
                "prohibido": False,
                "tipo": "seguimiento",
                "nombre": cliente.nombre,
            })
        
    def validar_pep(self, rut):
        #Llamada a API
        datos_pep = self.consulta_api_pep(rut)
        if datos_pep.get("coincidence") == "true":
            return Response({
                "rut": rut,
                "valido": True,
                "prohibido": True,
                "tipo": "pep",
                "nombre": datos_pep["info"]["name"]
            })
        
    def consulta_api_pep(self, rut):
        rut_para_regcheq = rut.replace(".","").replace("-","")
        token = "A4CF182C007DB3F9009B9666"
        url = f"https://external-api.regcheq.com/record/{token}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "dni": rut_para_regcheq,
            "personType": "natural"
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
            # Log detallado
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            if response.status_code != 200:
                print(f"Response Content: {response.text}")
            
                response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            print(f"Respuesta del servidor: {response.text}")
            return {"error": f"Error HTTP: {http_err}"}
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error de conexión: {conn_err}")
            return {"error": "No se pudo establecer conexión con la API"}
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout: {timeout_err}")
            return {"error": "Tiempo de espera agotado"}
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la solicitud: {req_err}")
            return {"error": "Error al procesar la solicitud"}
        except Exception as e:
            print(f"Error inesperado: {e}")
            return {"error": "Error desconocido"}
    
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