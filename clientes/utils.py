import requests
from datetime import datetime
from .models import Autoexcluidos

API_URL = 'https://autoexclusion.scj.gob.cl/api/v1/exclusions'
API_TOKEN = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJBcHAgRW50cmFkYXMiLCJpYXQiOjE3NTA5NTMwMjF9.24Xy25wCN5uj8JRtBF5Gr1ieF0HeDzn6qLjKyLHbTHU4mIrYe-UtsBzeMwr7nU2443_2pPInd2_4ec7thi5yAw'

def limpiar_rut(rut):
    return rut.replace('.', '').replace('-', '').strip()

def actualizar_autoexcluidos():
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Fallo al obtener datos de la API: {e}")
        return

    if not data:
        print("[INFO] No se recibieron datos de autoexcluidos.")
        return

    Autoexcluidos.objects.all().delete()  # 🧹 Limpia la tabla

    nuevos_registros = []

    for item in data:
        run = limpiar_rut(item.get("run", ""))
        nombre_completo = item.get("nombre", "")
        nombres = nombre_completo.split()

        nombre = " ".join(nombres[:2]) if len(nombres) >= 2 else nombre_completo
        apellido_pat = nombres[-2] if len(nombres) >= 3 else ""
        apellido_mat = nombres[-1] if len(nombres) >= 4 else ""

        assignee = item.get("assignee", {})
        ap_nombre_completo = assignee.get("nombre", "") or ""
        ap_nombres = ap_nombre_completo.split()

        nombre_ap = " ".join(ap_nombres[:2]) if len(ap_nombres) >= 2 else ap_nombre_completo
        apellido_pat_ap = ap_nombres[-2] if len(ap_nombres) >= 3 else ""
        apellido_mat_ap = ap_nombres[-1] if len(ap_nombres) >= 4 else ""

        fecha_ae_str = item.get("fecha_creacion")
        try:
            fecha_ae = datetime.fromisoformat(fecha_ae_str).date() if fecha_ae_str else None
        except:
            fecha_ae = None

        nuevos_registros.append(Autoexcluidos(
            rut=run,
            nombre=nombre,
            apellido_pat=apellido_pat,
            apellido_mat=apellido_mat,
            email=item.get("email"),
            telefono=item.get("telefono"),
            telefono_movil=item.get("telefono_movil"),
            ap_inscrito="1" if item.get("tiene_apoderado") else "0",
            ap_aceptado="1" if item.get("apoderado_validado") else "0",
            nombre_ap=nombre_ap,
            apellido_pat_ap=apellido_pat_ap,
            apellido_mat_ap=apellido_mat_ap,
            email_ap=assignee.get("email"),
            telefono_ap=assignee.get("phone"),
            telefono_movil_ap=assignee.get("mobile_phone"),
            activo="1",
            fecha_ae=fecha_ae,
        ))

    Autoexcluidos.objects.bulk_create(nuevos_registros)
    print(f"✅ Se actualizaron {len(nuevos_registros)} registros de autoexcluidos.")