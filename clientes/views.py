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
        return Response({
            "rut": rut,
            "valido": True,
            "mensaje": "RUT válido y sin alertas"
        }, status=status.HTTP_200_OK)

    # ---------- VALIDACIONES INDIVIDUALES -----------

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
            }, status=status.HTTP_200_OK)
        return None


    def validar_sospechoso(self, rut):
        cliente = Sospechosos.objects.filter(rut=rut).first()
        if cliente:
            return Response({
                "rut": rut,
                "valido": True,
                "tipo": "sospechoso",
                "nombre": cliente.nombre,
            }, status=status.HTTP_200_OK)
        return None

    def validar_autoexcluido(self, rut):
        cliente = Autoexcluidos.objects.filter(rut=rut).first()
        if cliente:
            return Response({
                "rut": rut,
                "valido": True,
                "tipo": "autoexcluido",
                "nombre": cliente.nombre,
                "desde": cliente.fecha_inicio,
                "hasta": cliente.fecha_termino,
            }, status=status.HTTP_200_OK)
        return None

    def validar_seguimiento(self, rut):
        cliente = Seguimientos.objects.filter(rut=rut).first()
        if cliente:
            return Response({
                "rut": rut,
                "valido": True,
                "tipo": "seguimiento",
                "nombre": cliente.nombre,
            }, status=status.HTTP_200_OK)
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
            return Response({
                "rut": rut_api,
                "valido": True,
                "tipo": "pep",
                "pep": True,
                "nombre": info.get("name"),
                "apellido": info.get("fatherName"),
                "cargo": info.get("position"),
                "nivel": info.get("level"),
            }, status=status.HTTP_200_OK)
        
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
