import requests
# NOTA: No necesitamos 'json' aquí, ya lo maneja requests.

def login(usuario, contrasena):
    """
    Envía los datos de login al servidor.
    Retorna el JSON de la respuesta si es exitosa, None si falla.
    """
    url = "http://127.0.0.1:5000/login" 
    data = {'username': usuario, 'password': contrasena}
    try:
        response = requests.post(url, json=data)
        
        # SI el status code es 200 (éxito), devuelve el JSON.
        if response.status_code == 200:
            return response.json()
        
        # SI el status code es 4xx o 5xx (error), lee el JSON para obtener el mensaje.
        else:
            # Esto maneja 401, 400, etc., y usa el mensaje del servidor.
            if response.json() and 'message' in response.json():
                 # Devuelve el mensaje de error específico del servidor (Contraseña incorrecta, Usuario no encontrado, etc.)
                return response.json()
            else:
                # Error desconocido o malformado
                print(f"Error HTTP desconocido: {response.status_code}")
                return {"message": f"Error de servidor: Código {response.status_code}"}
                
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        # Error de red (servidor apagado, URL incorrecta)
        return {"message": "Error de conexión con el servidor (servidor no activo)"}