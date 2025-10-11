from flask import Flask, request, jsonify
import bcrypt
import mysql.connector

# Importa tu archivo de base de datos
from database import connect_db

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
        # 🟢 CORRECCIÓN: Usar tabla 'candidatos', columna 'etapa_proceso' y 'fecha_postulacion'
        sql = "SELECT id_candidato AS id, nombre AS nombre, email, etapa_proceso AS estado, DATE_FORMAT(fecha_postulacion, '%%Y-%%m-%%d') AS fecha_post FROM candidatos"
        params = ()
        
        if estado_filtro and estado_filtro not in ["Todos los estados", ""]:
            sql += " WHERE etapa_proceso = %s" # 🟢 Corregido: La columna es 'etapa_proceso'
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
    nuevo_estado = data.get('estado') # El cliente envía 'estado'
    
    if not nuevo_estado:
        return jsonify({"message": "Falta el nuevo estado"}), 400

    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor()
        # 🟢 CORRECCIÓN: Usar tabla 'candidatos' y columna 'etapa_proceso'
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
        # 🟢 CORRECCIÓN: Usar columna 'nombre' (tu imagen lo confirma)
        sql = "SELECT id_empleado AS id, nombre AS nombre, sector FROM empleados"
        params = ()
        
        if nombre_filtro:
            sql += " WHERE nombre LIKE %s" # 🟢 Corregido: Columna es 'nombre'
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

# NOTA: La lógica de capacitaciones asume la existencia de tablas auxiliares, si fallan
# las consultas, revisa los nombres de 'empleado_capacitacion' y 'capacitaciones'.
@app.route('/api/empleados/<int:empleado_id>/capacitaciones', methods=['GET'])
def get_employee_capacitaciones(empleado_id):
    """Obtiene el historial de capacitaciones de un empleado específico."""
    # ... (Esta ruta se mantiene igual, ya que asume tablas de unión que no se ven en las imágenes) ...
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        # 🔴 Si esta consulta falla, revisa los nombres de las tablas 'empleado_capacitacion' y 'capacitaciones'
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


if __name__ == '__main__':
    if connect_db(DB_CONFIG):
        app.run(debug=True, port=5000)
    else:
        print("La aplicación no se pudo iniciar debido a un error de conexión con la base de datos.")