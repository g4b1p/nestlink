from flask import Flask, request, jsonify, send_from_directory
import os
import bcrypt
import mysql.connector

# Importa tu archivo de base de datos
from database import connect_db

# Crea la carpeta si no existe
UPLOAD_FOLDER = 'data/cvs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)

# Configuración de la base de datos (se usará en cada función)
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'nestlink_bd'
}

# =================================================================
# RUTA: /login
# =================================================================

@app.route('/login', methods=['POST'])
def login():
    """Maneja la autenticación de usuarios."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # ... (Validación y lógica sin cambios) ...

    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn:
             return jsonify({'message': 'Error de conexión con la BD'}), 500
             
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM usuarios WHERE nombre_usuario = %s" # Asumo que esta columna es correcta para 'usuarios'
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user: return jsonify({'message': 'Usuario no encontrado'}), 401

        # NOTA: Debes asegurarte de que 'contrasena_hash' contenga el hash de bcrypt
        hashed_password = user['contrasena_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return jsonify({
                'message': 'Login exitoso',
                'user_id': user['id_usuario'],
                'role': user['sector'],
                'username': user['nombre_usuario']
            }), 200
        else:
            return jsonify({'message': 'Contraseña incorrecta'}), 401

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return jsonify({'message': 'Error en el servidor'}), 500
    except Exception as e:
        print(f"Error inesperado en login: {e}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


# =================================================================
# RUTAS DEL MÓDULO DE RECURSOS HUMANOS
# =================================================================

@app.route('/api/candidatos', methods=['GET'])
def get_candidatos_list():
    """Obtiene la lista de candidatos/postulantes."""
    estado_filtro = request.args.get('estado')
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id_candidato AS id, nombre AS nombre, email, etapa_proceso AS estado, DATE_FORMAT(fecha_postulacion, '%%Y-%%m-%%d') AS fecha_post FROM candidatos"
        params = ()
        
        if estado_filtro and estado_filtro not in ["Todos los estados", ""]:
            sql += " WHERE etapa_proceso = %s"
            params = (estado_filtro,)

        cursor.execute(sql, params)
        candidatos = cursor.fetchall()
        
        return jsonify(candidatos), 200

    except Exception as e:
        print(f"Error al obtener candidatos: {e}")
        return jsonify({"message": "Error al consultar la base de datos de candidatos"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/api/candidatos/<int:postulante_id>', methods=['PUT'])
def update_postulante_state(postulante_id):
    """Actualiza la etapa_proceso de un candidato por ID."""
    data = request.get_json()
    nuevo_estado = data.get('estado')
    
    if not nuevo_estado:
        return jsonify({"message": "Falta el nuevo estado"}), 400

    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor()
        sql = "UPDATE candidatos SET etapa_proceso = %s WHERE id_candidato = %s" 
        cursor.execute(sql, (nuevo_estado, postulante_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Candidato no encontrado"}), 404
        
        return jsonify({"message": "Etapa de proceso actualizada correctamente"}), 200

    except Exception as e:
        print(f"Error al actualizar candidato {postulante_id}: {e}")
        return jsonify({"message": "Error al actualizar en la base de datos"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/api/empleados', methods=['GET'])
def get_empleados_list():
    """Obtiene la lista de empleados."""
    nombre_filtro = request.args.get('nombre')
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id_empleado AS id, nombre AS nombre, sector FROM empleados"
        params = ()
        
        if nombre_filtro:
            sql += " WHERE nombre LIKE %s"
            params = (f'%{nombre_filtro}%',)

        cursor.execute(sql, params)
        empleados = cursor.fetchall()
        
        return jsonify(empleados), 200

    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return jsonify({"message": "Error al consultar la base de datos de empleados"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# NOTA: La lógica de capacitaciones asume la existencia de tablas auxiliares.
@app.route('/api/empleados/<int:empleado_id>/capacitaciones', methods=['GET'])
def get_employee_capacitaciones(empleado_id):
    """Obtiene el historial de capacitaciones de un empleado específico."""
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT c.nombre_curso AS curso, DATE_FORMAT(ec.fecha_finalizacion, '%%Y-%%m-%%d') AS fecha
            FROM empleado_capacitacion ec
            JOIN capacitaciones c ON ec.id_capacitacion = c.id_capacitacion
            WHERE ec.id_empleado = %s
            ORDER BY ec.fecha_finalizacion DESC
        """
        cursor.execute(sql, (empleado_id,))
        capacitaciones = cursor.fetchall()
        
        return jsonify(capacitaciones), 200

    except Exception as e:
        print(f"Error al obtener capacitaciones para el empleado {empleado_id}: {e}")
        return jsonify({"message": "Error al consultar capacitaciones"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


# =================================================================
# RUTA: /api/candidatos/<id>/cv (PARA DESCARGAR/VER CV)
# =================================================================
@app.route('/api/candidatos/<int:candidato_id>/cv', methods=['GET'])
def get_candidato_cv(candidato_id):
    """Busca la ruta del CV en la BD y lo sirve al navegador."""
    conn = None
    try:
        # 🟢 CORRECCIÓN CLAVE: Usamos connect_db, igual que en las otras rutas
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        # 🟢 CORRECCIÓN: Usamos %s como marcador de posición para MySQL (no ?)
        cursor.execute("SELECT cv_path FROM candidatos WHERE id_candidato = %s", (candidato_id,))
        resultado = cursor.fetchone()
        cursor.close()

        if not resultado or not resultado['cv_path']:
            return jsonify({"message": f"CV no encontrado para candidato ID: {candidato_id} (Path no definido en BD)"}), 404

        # El resultado['cv_path'] es el nombre del archivo (ej: 'cv_1.pdf')
        filename = resultado['cv_path']

        # 3. Usar send_from_directory para enviar el archivo
        # UPLOAD_FOLDER debe ser el directorio definido al inicio (data/cvs)
        return send_from_directory(
            directory=UPLOAD_FOLDER,
            path=filename,
            as_attachment=False # False para mostrarlo en el navegador
        )
        
    except FileNotFoundError:
        # Esto ocurre si el archivo existe en la BD pero no en la carpeta data/cvs
        return jsonify({"message": f"El archivo '{filename}' no existe en el servidor (Carpeta: {UPLOAD_FOLDER})."}), 404
    except mysql.connector.Error as err:
        print(f"Error de base de datos al buscar CV: {err}")
        return jsonify({'message': 'Error de BD al buscar CV'}), 500
    except Exception as e:
        print(f"Error inesperado al servir el archivo: {e}")
        return jsonify({"message": f"Error al servir el archivo: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    # Creamos la carpeta UPLOAD_FOLDER por si acaso, antes de iniciar
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    if connect_db(DB_CONFIG):
        app.run(debug=True, port=5000)
    else:
        print("La aplicación no se pudo iniciar debido a un error de conexión con la base de datos.")