import mysql.connector

def connect_db(config):
    """
    Establece la conexión con la base de datos MySQL.
    """
    try:
        conn = mysql.connector.connect(**config)
        print("Conexión a la base de datos exitosa.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Ejemplo de uso (esto no es necesario en tu proyecto, solo para pruebas)
if __name__ == '__main__':
    # Sustituye con tus credenciales reales
    db_config_test = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'nestlink_bd'
    }
    connection = connect_db(db_config_test)
    if connection:
        connection.close()