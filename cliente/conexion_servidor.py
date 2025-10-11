import requests

def login(usuario, contrasena):
    # ... (Tu función de login se mantiene igual, ya que la ruta /login no cambió) ...
    url = "http://127.0.0.1:5000/login" 
    data = {'username': usuario, 'password': contrasena}
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            if response.json() and 'message' in response.json():
                return response.json()
            else:
                print(f"Error HTTP desconocido: {response.status_code}")
                return {"message": f"Error de servidor: Código {response.status_code}"}
                
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return {"message": "Error de conexión con el servidor (servidor no activo)"}

BASE_URL = "http://127.0.0.1:5000"

# =================================================================
# FUNCIONES DE OBTENCIÓN DE DATOS (GET)
# =================================================================

def get_candidatos(estado_filtro="Todos los estados"):
    """Obtiene la lista de candidatos desde el servidor."""
    url = f"{BASE_URL}/api/candidatos" # 🟢 Corregido: Llama a /api/candidatos
    params = {}
    if estado_filtro != "Todos los estados":
        params = {'estado': estado_filtro}
        
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener candidatos: {e}")
        return []

def get_empleados(nombre_filtro=""):
    """Obtiene la lista de empleados desde el servidor."""
    url = f"{BASE_URL}/api/empleados" # Correcto
    params = {}
    if nombre_filtro:
        params = {'nombre': nombre_filtro}
        
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener empleados: {e}")
        return []

def get_capacitaciones_empleado(empleado_id):
    """Obtiene el historial de capacitaciones de un empleado específico."""
    url = f"{BASE_URL}/api/empleados/{empleado_id}/capacitaciones" # Correcto
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener capacitaciones para el empleado {empleado_id}: {e}")
        return []

# =================================================================
# FUNCIONES DE ACCIÓN (PUT/POST)
# =================================================================

def actualizar_estado_candidato_db(id_candidato, etapa_proceso):
    """Envía una solicitud PUT para actualizar la etapa_proceso de un candidato."""
    url = f"{BASE_URL}/api/candidatos/{id_candidato}" # 🟢 Corregido: Llama a /api/candidatos
    # 🟢 IMPORTANTE: El backend espera 'estado' como clave en el JSON
    data = {'estado': etapa_proceso} 
    
    try:
        response = requests.put(url, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar el estado del candidato {id_candidato}: {e}")
        return False