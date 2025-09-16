from flask import Flask, request, jsonify
import bcrypt
import mysql.connector

# Importa tu archivo de base de datos
from database import connect_db



app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'user': 'root',
    'password': 'Cole481992_',
    'host': 'localhost', # O la IP de tu servidor MySQL
    'database': 'nestlink_bd'
}

# Conectar a la base de datos (puedes usar la función que creaste en database.py)
db = connect_db(DB_CONFIG)



@app.route('/login', methods=['POST'])
def login():
    # 1. Obtener los datos del cliente
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Validación básica
    if not username or not password:
        return jsonify({'message': 'Faltan usuario o contraseña'}), 400

    # 2. Conectar a la base de datos y buscar al usuario
    try:
        cursor = db.cursor(dictionary=True) # Usamos dictionary=True para obtener resultados como diccionarios
        sql = "SELECT * FROM usuarios WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 401 # 401 Unauthorized

        # 3. Verificar la contraseña
        # La contraseña en la BD debe estar hasheada. Por ejemplo: bcrypt.hashpw(b'password123', bcrypt.gensalt())
        hashed_password = user['password'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            # Login exitoso
            return jsonify({
                'message': 'Login exitoso',
                'user_id': user['id'],
                'role': user['role']
            }), 200 # 200 OK
        else:
            return jsonify({'message': 'Contraseña incorrecta'}), 401

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return jsonify({'message': 'Error en el servidor'}), 500
    
    
    if __name__ == '__main__':
        app.run(debug=True, port=5000)