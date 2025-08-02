from django.shortcuts import render
from django.http import JsonResponse
from clientes.models import Autoexcluidos
# Create your views here.

def index(request):
    return render(request, 'frontend/index.html')

def consultar_rut(request):
    rut = request.GET.get('rut')
    if rut:
        persona = Autoexcluidos.objects.filter(rut=rut).first()
        if persona:
            return JsonResponse({'status':'encontrado','tipo':'Autoexcluido'})
        else:
            return JsonResponse({'status':'no_encontrado'})
    return JsonResponse({'status':'error','mensaje':'Parámetro RUT faltante'})