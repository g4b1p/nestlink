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
ICON_MODULO_PRODUCCION = _load_icon('produccion-logo.png') 

# ÍCONOS PARA LA SIDEBAR
ICON_PRODUCTOS = _load_icon('gestion-productos.png') 
ICON_HISTORIAL_VENTAS = _load_icon('historial-ventas.png')

class ProduccionModule(BaseAppWindow):
    """Módulo de Producción."""
    
    MODULE_HEADER_ICON = ICON_MODULO_PRODUCCION

    def __init__(self, master, user_info):
        super().__init__(master, "Producción", user_info)
        
        # 1. Configuración de botones laterales
        self.button_config = [
            ("Gestión de Productos", self._show_productos_view, ICON_PRODUCTOS),
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
        """Muestra la interfaz para la gestión de productos (recetas, stock de materia prima)."""
        self._clear_main_content()
        self.main_content.grid_rowconfigure(0, weight=1)

        productos_frame = customtkinter.CTkFrame(self.main_content, fg_color=CONTENT_BG_COLOR, corner_radius=10)
        productos_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        productos_frame.grid_columnconfigure(0, weight=1) 
        
        customtkinter.CTkLabel(productos_frame, text="Gestión de Productos - Producción", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        customtkinter.CTkLabel(productos_frame, text="Implementación pendiente: Interfaz para gestionar las recetas de producción, el stock de insumos y registrar la finalización de lotes de productos.", text_color="gray").grid(row=1, column=0, padx=20, pady=(5, 20), sticky="w")

    def _show_historial_ventas_view(self):
        """Muestra el historial de ventas relevante para Producción (para planificación)."""
        self._clear_main_content()
        self.main_content.grid_rowconfigure(0, weight=1)

        historial_frame = customtkinter.CTkFrame(self.main_content, fg_color=CONTENT_BG_COLOR, corner_radius=10)
        historial_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        historial_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(historial_frame, text="Historial de Ventas - Planificación", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        customtkinter.CTkLabel(historial_frame, text="Implementación pendiente: Tabla para visualizar la demanda de productos históricos y así poder planificar la producción futura (usando 'get_historial_ventas').", text_color="gray").grid(row=1, column=0, padx=20, pady=(5, 20), sticky="w")