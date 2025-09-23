import requests
import json # No es necesario si ya se importa por Flask, pero es buena práctica

def login(usuario, contrasena):
    """
    Envía los datos de login al servidor.
    Retorna el JSON de la respuesta si es exitosa, None si falla.
    """
    # La URL de tu servidor debe ser la misma que usaste con curl
    url = "http://127.0.0.1:5000/login" 
    data = {'username': usuario, 'password': contrasena}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status() # Lanza un error para códigos de estado 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Error HTTP: {err}")
        return response.json() if response else {"message": "Error de servidor"}
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return {"message": "Error de conexión con el servidor"}