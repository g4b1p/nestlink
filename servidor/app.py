from flask import Flask, request, jsonify
import bcrypt
import mysql.connector

# Importa tu archivo de base de datos
from database import connect_db

app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'user': 'root',
    'password': '', # Asegúrate de que esta sea la contraseña correcta
    'host': 'localhost',
    'database': 'nestlink_bd'
}

# Conectar a la base de datos
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
        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 401

        # 3. Verificar la contraseña
        hashed_password = user['contrasena_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return jsonify({
                'message': 'Login exitoso',
                'user_id': user['id_usuario'],
                'role': user['sector']
            }), 200
        else:
            return jsonify({'message': 'Contraseña incorrecta'}), 401

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return jsonify({'message': 'Error en el servidor'}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)