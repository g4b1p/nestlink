import requests
import os # Necesario para verificar si el archivo existe y abrirlo

BASE_URL = "http://127.0.0.1:5000"

def login(usuario, contrasena):
    # ... (Tu función de login se mantiene igual, ya que la ruta /login no cambió) ...
    url = f"{BASE_URL}/login" 
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

# =================================================================
# FUNCIONES DE OBTENCIÓN DE DATOS (GET)
# =================================================================

def get_candidatos(estado_filtro="Todos los estados"):
    """Obtiene la lista de candidatos desde el servidor."""
    url = f"{BASE_URL}/api/candidatos"
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
    url = f"{BASE_URL}/api/empleados"
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
    url = f"{BASE_URL}/api/empleados/{empleado_id}/capacitaciones"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener capacitaciones para el empleado {empleado_id}: {e}")
        return []
        
def get_cv_candidato(candidato_id):
    """Obtiene la URL para ver el CV de un candidato."""
    url = f"{BASE_URL}/api/candidatos/{candidato_id}/cv"
    return url

# =================================================================
# FUNCIONES DE ACCIÓN (PUT/POST)
# =================================================================

def actualizar_estado_candidato_db(id_candidato, etapa_proceso):
    """Envía una solicitud PUT para actualizar la etapa_proceso de un candidato."""
    url = f"{BASE_URL}/api/candidatos/{id_candidato}"
    data = {'estado': etapa_proceso} 
    
    try:
        response = requests.put(url, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar el estado del candidato {id_candidato}: {e}")
        return False
        
# -----------------------------------------------------------------
# NUEVA FUNCIÓN: POST /api/candidatos (Añadir candidato con CV)
# -----------------------------------------------------------------
def post_nuevo_candidato(nombre, email, cv_filepath):
    """
    Envía los datos del formulario y el archivo CV al servidor usando multipart/form-data.
    
    :param cv_filepath: La ruta completa del archivo CV en el sistema local del cliente.
    """
    url = f"{BASE_URL}/api/candidatos"
    
    # 1. Preparar los datos del formulario (se envían como 'data' en requests)
    payload = {
        'nombre': nombre,
        'email': email,
    }

    files = {}
    file_pointer = None
    
    try:
        if cv_filepath:
            # Verificar si el archivo existe antes de intentar abrirlo
            if not os.path.exists(cv_filepath):
                return False, "Error: Archivo CV no encontrado en la ruta local."
            
            # 2. Preparar el archivo
            # Abrir el archivo en modo binario ('rb')
            file_pointer = open(cv_filepath, 'rb')
            
            # 'cv_file' debe coincidir con request.files.get('cv_file') en app.py
            files = {
                'cv_file': (os.path.basename(cv_filepath), file_pointer)
            }

        # 3. Enviar la petición POST
        # Usamos 'data' para el payload y 'files' para el archivo
        response = requests.post(url, data=payload, files=files)
        
        # 4. Manejar la respuesta
        if response.status_code in [201, 200]:
            return True, response.json().get('message', "Candidato guardado con éxito.")
        else:
            # Intentar obtener un mensaje de error del servidor si está disponible
            error_message = response.json().get('message', f"Error {response.status_code} al guardar candidato.") if response.content else f"Error HTTP: {response.status_code}"
            return False, error_message
            
    except requests.exceptions.RequestException as e:
        return False, f"Error de conexión con el servidor: {e}"
    except Exception as e:
        # Errores generales (ej. permiso denegado para abrir el archivo)
        return False, f"Error inesperado al procesar el archivo: {e}"
    finally:
        # Asegurarse de cerrar el puntero del archivo
        if file_pointer:
            file_pointer.close()