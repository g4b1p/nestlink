import customtkinter
from tkinter import messagebox
import os
from PIL import Image

# Importamos las dependencias clave
import conexion_servidor 

from base_module import BaseAppWindow, CELESTE_COLOR, SIDEBAR_COLOR, MAIN_BG_COLOR, CONTENT_BG_COLOR

# =================================================================
# CARGAR ÍCONOS DE MÓDULO (Asegúrate de tenerlos en la carpeta images/)
# =================================================================

_base_path = os.path.join(os.path.dirname(__file__), '..', 'images')

def _load_icon(filename, size=(30, 30)):
    """Función auxiliar para cargar íconos de forma segura."""
    try:
        return customtkinter.CTkImage(
            light_image=Image.open(os.path.join(_base_path, filename)),
            dark_image=Image.open(os.path.join(_base_path, filename)),
            size=size
        )
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el ícono '{filename}'. Usando None.")
        return None

# ÍCONO PARA EL HEADER
ICON_MODULO_LOGISTICA = _load_icon('logistica-logo.png') 

# ÍCONOS PARA LA SIDEBAR
ICON_PRODUCTOS = _load_icon('gestion-productos.png') 
ICON_CALENDARIO = _load_icon('calendario-logistico.png') # Nuevo ícono
ICON_HISTORIAL_VENTAS = _load_icon('historial-ventas.png')

class LogisticaModule(BaseAppWindow):
    """Módulo de Logística."""
    
    MODULE_HEADER_ICON = ICON_MODULO_LOGISTICA

    def __init__(self, master, user_info):
        super().__init__(master, "Logística", user_info)
        
        # 1. Configuración de botones laterales
        self.button_config = [
            ("Gestión de Productos", self._show_productos_view, ICON_PRODUCTOS),
            ("Calendario Logístico", self._show_calendario_view, ICON_CALENDARIO),
            ("Historial de Ventas", self._show_historial_ventas_view, ICON_HISTORIAL_VENTAS),
        ]
        
        # 2. Configurar y mostrar los botones
        self._set_sidebar_buttons(self.button_config)
        
        # 3. Mostrar la vista inicial por defecto
        self._show_productos_view() # Mostrar Productos como vista inicial

    # =================================================================
    # VISTAS
    # =================================================================

    def _show_productos_view(self):
        """Muestra la interfaz para la gestión de productos (principalmente stock e inventario)."""
        self._clear_main_content()
        self.main_content.grid_rowconfigure(0, weight=1)

        productos_frame = customtkinter.CTkFrame(self.main_content, fg_color=CONTENT_BG_COLOR, corner_radius=10)
        productos_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        productos_frame.grid_columnconfigure(0, weight=1) 
        
        customtkinter.CTkLabel(productos_frame, text="Gestión de Productos - Logística", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        customtkinter.CTkLabel(productos_frame, text="Implementación pendiente: Interfaz para gestionar el inventario, ubicaciones de almacén y actualizar el stock de productos (usando 'get_productos').", text_color="gray").grid(row=1, column=0, padx=20, pady=(5, 20), sticky="w")

    def _show_calendario_view(self):
        """Muestra la interfaz para el calendario de envíos y entregas."""
        self._clear_main_content()
        self.main_content.grid_rowconfigure(0, weight=1)

        calendario_frame = customtkinter.CTkFrame(self.main_content, fg_color=CONTENT_BG_COLOR, corner_radius=10)
        calendario_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        calendario_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(calendario_frame, text="Calendario Logístico", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        customtkinter.CTkLabel(calendario_frame, text="Implementación pendiente: Vista de calendario o lista de tareas para planificar y rastrear envíos y recepciones de pedidos/materiales.", text_color="gray").grid(row=1, column=0, padx=20, pady=(5, 20), sticky="w")

    def _show_historial_ventas_view(self):
        """Muestra el historial de ventas relevante para Logística (para gestión de pedidos)."""
        self._clear_main_content()
        self.main_content.grid_rowconfigure(0, weight=1)

        historial_frame = customtkinter.CTkFrame(self.main_content, fg_color=CONTENT_BG_COLOR, corner_radius=10)
        historial_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        historial_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(historial_frame, text="Historial de Ventas - Gestión de Pedidos", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        customtkinter.CTkLabel(historial_frame, text="Implementación pendiente: Tabla para revisar los pedidos (ventas) pendientes de envío y su estado logístico.", text_color="gray").grid(row=1, column=0, padx=20, pady=(5, 20), sticky="w")