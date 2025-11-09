from flask import Flask, request, jsonify, send_from_directory
import os
import bcrypt
import mysql.connector
from werkzeug.utils import secure_filename
from datetime import datetime
from decimal import Decimal

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

# Extensiones permitidas para el CV
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        sql = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
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

# -----------------------------------------------------------------
# NUEVA RUTA: POST /api/candidatos (Añadir nuevo candidato)
# -----------------------------------------------------------------
@app.route('/api/candidatos', methods=['POST'])
def add_candidato():
    """Recibe los datos del formulario (multipart/form-data) y el archivo CV."""
    conn = None
    file_save_path = None
    cv_path = None
    
    # 1. Obtener datos del formulario (request.form) y archivo (request.files)
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    cv_file = request.files.get('cv_file') # Nombre del campo esperado del cliente
    
    # Validaciones básicas
    if not nombre or not email:
        return jsonify({"message": "Nombre y email son obligatorios"}), 400

    try:
        if cv_file and cv_file.filename != '':
            if allowed_file(cv_file.filename):
                # 2. Guardar el archivo en el sistema de archivos
                filename = secure_filename(cv_file.filename)
                # Creamos un nombre único: (timestamp)_(nombre original)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                unique_filename = f"{timestamp}_{filename}"
                
                file_save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                cv_file.save(file_save_path)
                
                # Guardamos solo el nombre único del archivo para la BD
                cv_path = unique_filename
            else:
                 return jsonify({"message": "Tipo de archivo CV no permitido (solo PDF, PNG, JPG, JPEG, DOCX)"}), 400
        
        # 3. Conectar a la BD e Insertar el candidato
        conn = connect_db(DB_CONFIG)
        if not conn: 
            if file_save_path and os.path.exists(file_save_path): os.remove(file_save_path)
            return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor()
        
        # Insertamos el candidato con el cv_path (que puede ser NULL si no subió archivo)
        sql = """
            INSERT INTO candidatos (nombre, email, etapa_proceso, fecha_postulacion, cv_path)
            VALUES (%s, %s, %s, CURDATE(), %s)
        """
        # El estado inicial siempre será 'Recibido'
        cursor.execute(sql, (nombre, email, "Recibido", cv_path))
        conn.commit()
        
        return jsonify({"message": "Candidato registrado exitosamente"}), 201

    except Exception as e:
        print(f"Error al agregar candidato: {e}")
        # Si la inserción a BD falla o hay otro error, borrar el archivo guardado (si existe)
        if file_save_path and os.path.exists(file_save_path):
             os.remove(file_save_path)
        return jsonify({"message": "Error al procesar el registro del candidato"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------
# RUTA: GET /api/candidatos (Obtener lista de candidatos)
# -----------------------------------------------------------------
@app.route('/api/candidatos', methods=['GET'])
def get_candidatos_list():
    """Obtiene la lista de candidatos/postulantes."""
    estado_filtro = request.args.get('estado')
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id_candidato AS id, nombre AS nombre, email, etapa_proceso AS estado, DATE_FORMAT(fecha_postulacion, '%Y-%m-%d') AS fecha_post FROM candidatos"
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


# -----------------------------------------------------------------
# RUTA: PUT /api/candidatos/<id> (Actualizar estado)
# -----------------------------------------------------------------
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


# -----------------------------------------------------------------
# RUTA: GET /api/empleados
# -----------------------------------------------------------------
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

# -----------------------------------------------------------------
# RUTA: GET /api/empleados/<id>/capacitaciones
# -----------------------------------------------------------------
@app.route('/api/empleados/<int:empleado_id>/capacitaciones', methods=['GET'])
def get_employee_capacitaciones(empleado_id):
    """Obtiene el historial de capacitaciones de un empleado específico."""
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT c.nombre_curso AS curso, DATE_FORMAT(ec.fecha_finalizacion, '%Y-%m-%d') AS fecha
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


# -----------------------------------------------------------------
# RUTA: GET /api/candidatos/<id>/cv (PARA DESCARGAR/VER CV)
# -----------------------------------------------------------------
@app.route('/api/candidatos/<int:candidato_id>/cv', methods=['GET'])
def get_candidato_cv(candidato_id):
    """Busca la ruta del CV en la BD y lo sirve al navegador."""
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT cv_path FROM candidatos WHERE id_candidato = %s", (candidato_id,))
        resultado = cursor.fetchone()
        cursor.close()

        if not resultado or not resultado['cv_path']:
            return jsonify({"message": f"CV no encontrado para candidato ID: {candidato_id} (Path no definido en BD)"}), 404

        filename = resultado['cv_path']

        return send_from_directory(
            directory=UPLOAD_FOLDER,
            path=filename,
            as_attachment=False
        )
        
    except FileNotFoundError:
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

# =================================================================
# RUTAS DEL MÓDULO DE VENTAS
# =================================================================

# -----------------------------------------------------------------
# RUTA: GET /api/productos (Obtener lista de productos)
# -----------------------------------------------------------------
@app.route('/api/productos', methods=['GET'])
def get_productos_list():
    """Obtiene la lista de productos, con opción a filtrar por estado."""
    estado_filtro = request.args.get('estado')
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor(dictionary=True)
        
        # 🚨 NOTA IMPORTANTE: Los nombres de las columnas deben coincidir con tu tabla 'productos'
        sql = """
            SELECT 
                id_producto AS id, 
                nombre, 
                estado, 
                precio_unitario AS precio, 
                stock, 
                categoria,
                lote
            FROM productos
        """
        params = ()
        
        if estado_filtro and estado_filtro not in ["Todos los estados", ""]:
            sql += " WHERE estado = %s"
            params = (estado_filtro,)
            
        sql += " ORDER BY nombre ASC" # Ordenar alfabéticamente
        
        cursor.execute(sql, params)
        productos = cursor.fetchall()
        
        return jsonify(productos), 200

    except mysql.connector.Error as err:
        print(f"Error de base de datos al obtener productos: {err}")
        return jsonify({"message": "Error al consultar la base de datos de productos"}), 500
    except Exception as e:
        print(f"Error inesperado al obtener productos: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------
# RUTA: POST /api/productos (Registrar un nuevo producto)
# -----------------------------------------------------------------
@app.route('/api/productos', methods=['POST'])
def create_producto():
    """Inserta un nuevo producto en la tabla productos."""
    data = request.get_json()
    
    nombre = data.get('nombre')
    categoria = data.get('categoria')
    precio = data.get('precio_unitario')
    stock = data.get('stock')
    estado = data.get('estado')
    lote = data.get('lote')

    # Validación básica (aunque el cliente ya lo hizo, es vital en el servidor)
    if not all([nombre, categoria, precio is not None, stock is not None, estado, lote]):
        return jsonify({"message": "Faltan datos obligatorios para registrar el producto"}), 400

    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor()
        
        # 1. Verificar si ya existe un producto con el mismo nombre (ejemplo de unicidad)
        cursor.execute("SELECT id_producto FROM productos WHERE nombre = %s", (nombre,))
        if cursor.fetchone():
            return jsonify({"message": f"Ya existe un producto registrado con el nombre '{nombre}'."}), 409 # Conflict

        # 2. Insertar el nuevo producto
        sql = """
            INSERT INTO productos (nombre, categoria, precio_unitario, stock, estado, lote)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (nombre, categoria, precio, stock, estado, lote)
        
        cursor.execute(sql, params)
        conn.commit()
        
        return jsonify({"message": "Producto registrado correctamente", "id": cursor.lastrowid}), 201 # Created

    except mysql.connector.Error as err:
        print(f"Error de base de datos al registrar producto: {err}")
        return jsonify({"message": "Error al registrar en la base de datos"}), 500
    except Exception as e:
        print(f"Error inesperado al registrar producto: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------
# RUTA: PUT /api/productos/<id> (Actualizar datos de un producto)
# -----------------------------------------------------------------
@app.route('/api/productos/<int:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    """Actualiza los campos editables de un producto por ID."""
    data = request.get_json()
    
    # Campos que esperamos actualizar (NOMBRES DE COLUMNAS EN LA BD)
    precio = data.get('precio_unitario')
    stock = data.get('stock')
    estado = data.get('estado')
    lote = data.get('lote')

    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: return jsonify({"message": "Error de conexión con la BD"}), 500

        cursor = conn.cursor()
        
        sql = """
            UPDATE productos 
            SET precio_unitario = %s, stock = %s, estado = %s, lote = %s
            WHERE id_producto = %s
        """
        params = (precio, stock, estado, lote, producto_id)
        
        cursor.execute(sql, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Producto no encontrado o datos idénticos"}), 404
        
        return jsonify({"message": "Producto actualizado correctamente"}), 200

    except mysql.connector.Error as err:
        print(f"Error de base de datos al actualizar producto {producto_id}: {err}")
        return jsonify({"message": "Error al actualizar en la base de datos"}), 500
    except Exception as e:
        print(f"Error inesperado al actualizar producto: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/api/ventas', methods=['POST'])
def registrar_venta():
    """
    Endpoint para registrar una nueva venta y actualizar el stock.
    Inserta directamente en la tabla 'ventas' (estructura denormalizada).
    """
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad')
    
    id_cliente_recibido = data.get('id_cliente') 
    id_vendedor_recibido = data.get('id_vendedor')

    # Validaciones iniciales
    if not producto_id or not cantidad:
        return jsonify({"message": "Faltan producto_id o cantidad."}), 400
    
    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return jsonify({"message": "La cantidad debe ser un número positivo."}), 400
    except ValueError:
        return jsonify({"message": "La cantidad debe ser un número entero válido."}), 400

    conn = None
    cursor = None
    
    try:
        conn = connect_db(DB_CONFIG) 
        if not conn:
            return jsonify({"message": "Error de conexión con la BD"}), 500
            
        cursor = conn.cursor(dictionary=True) 

        # 1. Verificar Stock, Precio y Categoría del producto
        cursor.execute("SELECT stock, precio_unitario, categoria FROM productos WHERE id_producto = %s", (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            return jsonify({"message": f"Producto con ID {producto_id} no encontrado."}), 404
        
        stock_actual = producto['stock']
        precio_unitario = producto['precio_unitario'] # Objeto Decimal
        categoria_producto = producto['categoria']   # Obtenemos la categoría
        
        if stock_actual < cantidad:
            return jsonify({"message": "Stock insuficiente para realizar la venta."}), 400
            
        id_cliente = id_cliente_recibido 
        id_vendedor = id_vendedor_recibido
        
        subtotal = precio_unitario * cantidad 
        iva = subtotal * Decimal('0.16') # Usamos Decimal
        total_venta = subtotal + iva
        fecha_venta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 3. Registrar la Venta (Inserción ÚNICA)
        # 🚨 CAMBIO DE LÓGICA: Insertamos todo en la tabla 'ventas'
        sql_insert_venta = """
            INSERT INTO ventas (
                id_producto, categoria, id_cliente, id_usuario_vendedor, 
                cantidad, fecha_venta, monto_total
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql_insert_venta, 
            (
                producto_id, categoria_producto, id_cliente, id_vendedor, 
                cantidad, fecha_venta, total_venta
            )
        )
        id_venta_creada = cursor.lastrowid

        # 4. Actualizar el Stock del Producto
        nuevo_stock = stock_actual - cantidad
        cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", (nuevo_stock, producto_id))

        conn.commit()
        return jsonify({"message": "Venta registrada y stock actualizado con éxito.", "id_venta": id_venta_creada}), 201

    except mysql.connector.Error as err:
        if conn: conn.rollback()
        print(f"Error en la transacción de venta (BD): {err}")
        if err.errno == 1452:
             return jsonify({"message": f"Error de BD: Clave foránea fallida. Revise si el cliente ID={id_cliente} o vendedor ID={id_vendedor} existen."}), 500
        return jsonify({"message": f"Error de base de datos al registrar venta: {err}"}), 500
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error inesperado en transacción de venta: {e}")
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500
        
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()


@app.route('/api/clientes', methods=['GET'])
def get_clientes_list():
    """Obtiene la lista de todos los clientes para los OptionMenu."""
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: 
            return jsonify({"message": "Error de conexión con la BD"}), 500
            
        cursor = conn.cursor(dictionary=True)
        # 🚨 Asegúrate que tu tabla se llame 'clientes' y las columnas 'id_cliente', 'nombre'
        cursor.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre ASC")
        clientes = cursor.fetchall()
        
        return jsonify(clientes), 200

    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/api/campañas', methods=['GET'])
def get_campañas_list():
    """Obtiene la lista de campañas, con filtro opcional por nombre."""
    
    # Obtenemos el parámetro de búsqueda (si existe)
    nombre_filtro = request.args.get('nombre')
    
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: 
            return jsonify({"message": "Error de conexión con la BD"}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # 🚨 Columnas de tu tabla 'campanas' (basado en tu screenshot)
        sql = """
            SELECT 
                id_campana, 
                nombre_campana, 
                objetivo, 
                DATE_FORMAT(fecha_inicio, '%Y-%m-%d') as fecha_inicio, 
                DATE_FORMAT(fecha_fin, '%Y-%m-%d') as fecha_fin, 
                resultados 
            FROM campanas
        """
        params = ()
        
        if nombre_filtro:
            sql += " WHERE nombre_campana LIKE %s"
            params = (f'%{nombre_filtro}%',)
            
        sql += " ORDER BY fecha_inicio DESC" # Ordenar por más recientes
        
        cursor.execute(sql, params)
        campañas = cursor.fetchall()
        
        return jsonify(campañas), 200

    except mysql.connector.Error as err:
        print(f"Error de base de datos al obtener campañas: {err}")
        return jsonify({"message": f"Error de BD: {err}"}), 500
    except Exception as e:
        print(f"Error inesperado al obtener campañas: {e}")
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


# Archivo: app.py (AÑADIR esta nueva ruta)

@app.route('/api/campañas/<int:campana_id>', methods=['PUT'])
def update_campana(campana_id):
    """Actualiza los datos de una campaña específica."""
    data = request.json
    
    # Campos que el cliente puede enviar para actualizar
    objetivo = data.get('objetivo')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    resultados = data.get('resultados')
    
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: 
            return jsonify({"message": "Error de conexión con la BD"}), 500
            
        cursor = conn.cursor()

        # Construir la consulta de actualización. 
        # NOTA: nombre_campana e id_campana NO se actualizan.
        sql = """
            UPDATE campanas 
            SET objetivo = %s, fecha_inicio = %s, fecha_fin = %s, resultados = %s
            WHERE id_campana = %s
        """
        params = (objetivo, fecha_inicio, fecha_fin, resultados, campana_id)
        
        cursor.execute(sql, params)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": f"Campaña con ID {campana_id} no encontrada o sin cambios."}), 404
            
        return jsonify({"message": f"Campaña '{campana_id}' actualizada con éxito."}), 200

    except mysql.connector.Error as err:
        print(f"Error de base de datos al actualizar campaña: {err}")
        return jsonify({"message": f"Error de BD: {err}"}), 500
    except Exception as e:
        print(f"Error inesperado al actualizar campaña: {e}")
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/api/ventas', methods=['GET'])
def get_ventas_historial():
    """Obtiene el historial completo de ventas, con nombres de tablas relacionadas y filtro por categoría."""
    
    # Obtener el parámetro de filtro de categoría (si existe)
    categoria_filtro = request.args.get('categoria')
    
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: 
            return jsonify({"message": "Error de conexión con la BD"}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # 🚨 CONSULTA SQL CON JOINS PARA OBTENER LOS NOMBRES 🚨
        sql = """
            SELECT 
                v.id_venta, 
                p.nombre AS nombre_producto, 
                v.categoria, 
                v.cantidad, 
                DATE_FORMAT(v.fecha_venta, '%Y-%m-%d %H:%i') AS fecha_venta, 
                c.nombre AS nombre_cliente, 
                e.nombre AS nombre_vendedor, 
                v.monto_total
            FROM ventas v
            JOIN productos p ON v.id_producto = p.id_producto
            JOIN clientes c ON v.id_cliente = c.id_cliente
            JOIN empleados e ON v.id_usuario_vendedor = e.id_empleado
        """
        params = ()
        
        if categoria_filtro and categoria_filtro != 'Todas':
            sql += " WHERE v.categoria = %s"
            params = (categoria_filtro,)
            
        sql += " ORDER BY v.fecha_venta DESC" # Ordenar por más recientes
        
        cursor.execute(sql, params)
        historial_ventas = cursor.fetchall()
        
        return jsonify(historial_ventas), 200

    except mysql.connector.Error as err:
        print(f"Error de base de datos al obtener historial de ventas: {err}")
        return jsonify({"message": f"Error de BD: {err}"}), 500
    except Exception as e:
        print(f"Error inesperado al obtener historial de ventas: {e}")
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# También necesitamos una ruta para obtener las categorías para el filtro
@app.route('/api/categorias_ventas', methods=['GET'])
def get_categorias_ventas():
    """Obtiene una lista única de categorías usadas en la tabla ventas."""
    conn = None
    try:
        conn = connect_db(DB_CONFIG)
        if not conn: 
            return jsonify({"message": "Error de conexión con la BD"}), 500
        
        cursor = conn.cursor()
        # Selecciona las categorías únicas y no nulas
        cursor.execute("SELECT DISTINCT categoria FROM ventas WHERE categoria IS NOT NULL")
        categorias = [row[0] for row in cursor.fetchall()]
        return jsonify(categorias), 200
        
    except mysql.connector.Error as err:
        print(f"Error de base de datos al obtener categorías: {err}")
        return jsonify({"message": f"Error de BD: {err}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    # Creamos la carpeta UPLOAD_FOLDER por si acaso, antes de iniciar
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    if connect_db(DB_CONFIG):
        # Asegúrate de ejecutar el servidor en el modo correcto
        app.run(debug=True, port=5000)
    else:
        print("La aplicación no se pudo iniciar debido a un error de conexión con la base de datos.")
