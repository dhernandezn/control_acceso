from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Prohibidos, Seguimientos, Peps, Sospechosos, Autoexcluidos
from datetime import date
import requests

class ValidarRutView(APIView):

    def post(self, request):
        rut = request.data.get('rut', '')
        if not self.validar_rut(rut):
            return Response({
                "rut": rut,
                "valido": False,
                "mensaje": "Rut inválido"
            }, status=status.HTTP_200_OK)

        rut_limpio = rut.replace(".", "").upper()
        rut_api = rut_limpio.replace("-", "")

        # Validaciones en orden
        validaciones = [
            lambda: self.validar_prohibido(rut_limpio),
            lambda: self.validar_sospechoso(rut_limpio),
            lambda: self.validar_autoexcluido(rut_limpio),
            lambda: self.validar_seguimiento(rut_limpio),
            lambda: self.validar_pep(rut_api),
        ]

        for validar in validaciones:
            resultado = validar()
            if resultado:
                return resultado

        # Si ninguna validación aplica
        respuesta = self.respuesta_base(rut)
        respuesta["valido"] = True
        respuesta["rut"] = rut
        return Response(respuesta, status=status.HTTP_200_OK)

    # ---------- VALIDACIONES INDIVIDUALES -----------

    def validar_prohibido(self, rut):
        cliente = Prohibidos.objects.filter(rut=rut).first()
        if cliente and cliente.fecha_inicio <= date.today() <= cliente.fecha_termino:
            respuesta = self.respuesta_base(rut)
            respuesta["prohibido"] = True
            respuesta["nombre"] = cliente.nombre
            respuesta["desde"] = cliente.fecha_inicio
            respuesta["hasta"] = cliente.fecha_termino
            return Response(respuesta, status=status.HTTP_200_OK)
        return None


    def validar_sospechoso(self, rut):
        cliente = Sospechosos.objects.filter(rut=rut).first()
        if cliente:
            respuesta = self.respuesta_base(rut)
            respuesta["sospechoso"] = True
            respuesta["nombre"] = cliente.nombre
            return Response(respuesta, status=status.HTTP_200_OK)
        return None

    def validar_autoexcluido(self, rut):
        cliente = Autoexcluidos.objects.filter(rut=rut).first()
        if cliente:
            respuesta = self.respuesta_base(rut)
            respuesta["autoexcluido"] = True
            respuesta["nombre"] = cliente.nombre
            respuesta["apellido"] = cliente.apellido_pat
            respuesta["desde"] = cliente.fecha_ae
            return Response(respuesta, status=status.HTTP_200_OK)
        return None

    def validar_seguimiento(self, rut):
        cliente = Seguimientos.objects.filter(rut=rut).first()
        if cliente:
            respuesta = self.respuesta_base(rut)
            respuesta["seguimiento"] = True
            respuesta["nombre"] = cliente.nombre
            return Response(respuesta, status=status.HTTP_200_OK)
        return None

    def validar_pep(self, rut_api):
        resultado = self.consulta_api_pep(rut_api)
        if not resultado or "listas" not in resultado:
            return None
        listas = resultado.get("listas", {})
        pep_chile = listas.get("pepChile", {})
        pep_data = pep_chile.get("data", {})

        es_pep = pep_data.get("listResult", False)

        if es_pep:
            info = pep_data.get("info", {})
            respuesta = self.respuesta_base(rut_api)
            respuesta["pep"] = True
            respuesta["nombre"] = info.get("name")
            respuesta["apellido"] = info.get("fatherName")
            respuesta["cargo"] = info.get("position")
            respuesta["nivel"] = info.get("level")
            if info.get("level") == "Indirecto":
                respuesta["pep_relacionado"] = info.get("relatedPepName")
                respuesta["relacion"] = info.get("relation")
            return Response(respuesta, status=status.HTTP_200_OK)
        
        return None

    # ---------- CONSULTA EXTERNA PEP -----------

    def consulta_api_pep(self, rut):
        token = 'A4CF182C007DB3F9009B9666'
        url = f'https://external-api.regcheq.com/record/{token}'
        headers = {'Content-Type': 'application/json'}
        data = {'dni': rut, 'personType': 'natural'}

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print("❌ Excepción al consultar API:", str(e))
        return {}

    # ---------- VALIDACIÓN RUT CHILENO -----------

    def validar_rut(self, rut):
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

    def respuesta_base(self, rut):
        return {
            "rut": rut,
            "valido": True,
            "prohibido": False,
            "sospechoso": False,
            "seguimiento": False,
            "autoexcluido": False,
            "pep": False,
            "nombre": "",
            "desde": None,
            "hasta": None,
            "apellido": "",
            "cargo": "",
            "nivel": "",
            "pep_relacionado":"",
            "relacion": "",
        }
