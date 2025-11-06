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

def get_productos(estado_filtro="Todos los estados"):
    """Obtiene la lista de productos desde el servidor, filtrando opcionalmente por estado."""
    url = f"{BASE_URL}/api/productos" 
    params = {}
    if estado_filtro != "Todos los estados":
        params = {'estado': estado_filtro}
        
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json() 
    
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos: {e}")
        # En caso de error de conexión o API, devuelve una lista vacía.
        return []

def update_producto(producto_id, data):
    """Actualiza los datos de un producto por ID."""
    url = f"{BASE_URL}/api/productos/{producto_id}"
    
    try:
        response = requests.put(url, json=data)
        response.raise_for_status() 
        
        return True, "Producto actualizado correctamente."

    except requests.exceptions.HTTPError as e:
        error_message = response.json().get('message', 'Error desconocido al actualizar.')
        print(f"Error HTTP al actualizar producto: {e}")
        return False, error_message
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al actualizar producto: {e}")
        return False, f"Error de conexión con el servidor: {e}"

def create_producto(data):
    """Crea un nuevo producto enviando una solicitud POST al servidor."""
    url = f"{BASE_URL}/api/productos"
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status() 
        
        return True, "Producto registrado correctamente."

    except requests.exceptions.HTTPError as e:
        error_message = response.json().get('message', 'Error desconocido al registrar.')
        print(f"Error HTTP al registrar producto: {e}")
        return False, error_message
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al registrar producto: {e}")
        return False, f"Error de conexión con el servidor: {e}"

# Archivo: conexion_servidor.py (REEMPLAZAR esta función)

def register_sale(sale_data):
    """
    Registra una nueva venta en el servidor (POST /api/ventas).
    Espera sale_data = {"producto_id": id, "cantidad_vendida": cant, "id_cliente": id}
    """
    url = f"{BASE_URL}/api/ventas"
    
    # 🚨 CAMBIO: El payload ahora incluye el id_cliente
    payload = {
        "producto_id": sale_data["producto_id"],
        "cantidad": sale_data["cantidad_vendida"],
        "id_cliente": sale_data["id_cliente"] # <-- ID de cliente real
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True, response.json().get("message", "Venta registrada con éxito.")
    # ... (El resto del manejo de errores sigue igual) ...
    except requests.exceptions.HTTPError as e:
        try:
            error_message = response.json().get('message', f'Error HTTP {response.status_code}.')
        except requests.exceptions.JSONDecodeError:
            error_message = f"Error {response.status_code}: {response.text}"
        print(f"Error HTTP al registrar venta: {error_message}")
        return False, error_message
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al registrar venta: {e}")
        return False, f"Error de conexión con el servidor: {e}"

def get_clientes():
    """Obtiene la lista de clientes (ID y Nombre) desde el servidor."""
    url = f"{BASE_URL}/api/clientes"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener clientes: {e}")
        return []