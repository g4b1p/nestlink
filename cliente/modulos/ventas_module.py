import customtkinter
from tkinter import messagebox
import os
from PIL import Image

# Importamos las dependencias clave
import conexion_servidor 

# Importación de la clase base y los colores
from base_module import BaseAppWindow, CELESTE_COLOR, SIDEBAR_COLOR, MAIN_BG_COLOR

# =================================================================
# CARGAR ÍCONOS DE MÓDULO (Asegúrate de tenerlos en la carpeta images/)
# =================================================================

_base_path = os.path.join(os.path.dirname(__file__), '..', 'images')

# 🚨 ÍCONO PARA EL HEADER (ventas-logo.png)
ICON_MODULO_VENTAS = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'ventas-logo.png')),
    dark_image=Image.open(os.path.join(_base_path, 'ventas-logo.png')),
    size=(30, 30)
)

# ÍCONOS PARA LA SIDEBAR (Basados en el Mockup)
ICON_PRODUCTOS = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'gestion-productos.png')),
    dark_image=Image.open(os.path.join(_base_path, 'gestion-productos.png')),
    size=(30, 30)
)

ICON_RENDIMIENTO = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'panel-rendimiento.png')),
    dark_image=Image.open(os.path.join(_base_path, 'panel-rendimiento.png')),
    size=(30, 30)
)

ICON_CAMPAÑAS = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'gestion-campañas.png')),
    dark_image=Image.open(os.path.join(_base_path, 'gestion-campañas.png')),
    size=(30, 30)
)

ICON_HISTORIAL = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'historial-ventas.png')),
    dark_image=Image.open(os.path.join(_base_path, 'historial-ventas.png')),
    size=(30, 30)
)

# =================================================================
# CLASE ESPECÍFICA PARA VENTAS
# =================================================================

class VentasModule(BaseAppWindow):
    """Módulo para Ventas, gestionando Productos, Rendimiento, Campañas e Historial."""

    # Asignación del ícono al header
    MODULE_HEADER_ICON = ICON_MODULO_VENTAS

    # Asignación de íconos locales para el sidebar
    ICON_PRODUCTOS = ICON_PRODUCTOS 
    ICON_RENDIMIENTO = ICON_RENDIMIENTO
    ICON_CAMPAÑAS = ICON_CAMPAÑAS
    ICON_HISTORIAL = ICON_HISTORIAL

    def __init__(self, master, user_info):

        super().__init__(master, "Ventas", user_info)

        # Configuración de los botones de la barra lateral
        self.button_config = [
            ("Gestión de Productos", self._show_productos_view, self.ICON_PRODUCTOS),
            ("Panel de Rendimiento", self._show_rendimiento_view, self.ICON_RENDIMIENTO),
            ("Gestión de Campañas", self._show_campañas_view, self.ICON_CAMPAÑAS),
            ("Historial de Ventas", self._show_historial_view, self.ICON_HISTORIAL),
        ]

        # Establece la primera vista como activa por defecto (Gestión de Productos)
        if self.button_config:
            self.active_view = self.button_config[0][0]

        # Esto construye la barra lateral con los estilos activo/inactivo
        self._set_sidebar_buttons(self.button_config)

        # Llama a la función de la primera vista para que se cargue la tabla
        if self.button_config and self.button_config[0][1]:
            self.button_config[0][1]()


    # -----------------------------------------------------------------
    # VISTA 1: GESTIÓN DE PRODUCTOS (Replicando diseño de RRHH)
    # -----------------------------------------------------------------

    def _show_productos_view(self):
        """Muestra la interfaz para la gestión y listado de productos."""
        self._clear_main_content()

        # Configuración de expansión (Fila 1 para la tabla, se expande)
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # --- 1. Header de la Vista (Título, Botón Agregar y Filtro) ---
        view_header_frame = customtkinter.CTkFrame(self.main_content, fg_color="transparent")
        view_header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        view_header_frame.grid_columnconfigure(0, weight=1) # Título expande
        view_header_frame.grid_columnconfigure(1, weight=0) # Filtro no expande
        view_header_frame.grid_columnconfigure(2, weight=0) # Botón no expande

        customtkinter.CTkLabel(
            view_header_frame,
            text="Gestión de Productos",
            font=customtkinter.CTkFont(size=20, weight="bold"), 
            text_color="#5b94c6" 
        ).grid(row=0, column=0, sticky="w")

        # Filtro de Estado (CTkOptionMenu)
        estados = ["Todos los estados", "Listo para distribución", "En revisión de calidad", "En embalaje", "Agotado"]
        self.productos_filtro = customtkinter.CTkOptionMenu(
            view_header_frame,
            values=estados,
            command=self._filtrar_productos_tabla,
            width=220 # Ancho ajustado para texto
        )
        self.productos_filtro.grid(row=0, column=1, padx=(0, 15), sticky="e")

        # Botón Agregar Producto
        customtkinter.CTkButton(
            view_header_frame,
            text="+ Agregar Producto",
            command=self._open_agregar_producto_modal,
            fg_color="#00bf63", # Color verde, coherente con RRHH
            hover_color="#00994f",
            height=35,
            anchor="center"
        ).grid(row=0, column=2, sticky="e")

        # -----------------------------------------------------------------------
        # 2. Área de la Tabla (Contenedor con Borde, Cabecera FIJA y ScrollableFrame)
        # -----------------------------------------------------------------------

        # PASO 1: Contenedor que maneja el Borde (Fila 1 del main_content)
        self.table_border_container = customtkinter.CTkFrame(
            self.main_content,
            corner_radius=5,
            fg_color=MAIN_BG_COLOR,
            border_color="#5b94c6",
            border_width=2
        )
        self.table_border_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.table_border_container.grid_columnconfigure(0, weight=1)
        self.table_border_container.grid_rowconfigure(0, weight=0) # Cabecera fija
        self.table_border_container.grid_rowconfigure(1, weight=1) # Cuerpo scrollable

        # Definición de las columnas de la tabla de productos
        columnas = ["Nombre", "Estado", "Precio", "Stock", "Categoría", "Acciones"]
        NUM_COLUMNAS_DATOS = len(columnas)

        # 🚨 PASO 2: Frame para la CABECERA FIJA
        self.header_fixed_frame = customtkinter.CTkFrame(
            self.table_border_container,
            fg_color="#5b94c6", # Color Azul de la Cabecera
            corner_radius=0
        )
        self.header_fixed_frame.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))

        # CLAVE A: COMPENSACIÓN SCROLLBAR (Columna extra con minsize=17)
        self.header_fixed_frame.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17)

        # BUCLE DE CONFIGURACIÓN Y ETIQUETAS DEL ENCABEZADO
        # Definimos los pesos de expansión de las columnas para alineación
        column_weights = [3, 2, 1, 1, 2, 0] # Nombre expande más (3), Precio/Stock menos (1), Acciones no (0)

        for i, col_name in enumerate(columnas):
            self.header_fixed_frame.grid_columnconfigure(i, weight=column_weights[i])
            customtkinter.CTkLabel(
                self.header_fixed_frame,
                text=col_name,
                font=customtkinter.CTkFont(weight="bold", size=13),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")


        # 🚨 PASO 3: CTkScrollableFrame (la tabla de datos) 
        self.productos_tabla_frame = customtkinter.CTkScrollableFrame(
            self.table_border_container,
            fg_color="transparent"
        )
        self.productos_tabla_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))

        # CLAVE C: Configuramos las columnas del cuerpo para que coincidan con la cabecera.
        for i in range(len(columnas)):
            self.productos_tabla_frame.grid_columnconfigure(i, weight=column_weights[i])

        # Finalmente, cargamos los datos
        self._load_productos_data(estado_filtro=self.productos_filtro.get())


    def _load_productos_data(self, estado_filtro):
        """Carga datos del servidor (BD) y construye las filas de datos de productos."""
        # Limpiamos el contenido anterior
        for widget in self.productos_tabla_frame.winfo_children():
            widget.destroy()

        # --- Obtención de Datos DEL SERVIDOR ---
        try:
            # Asumimos que existe una función similar a get_candidatos en conexion_servidor
            productos = conexion_servidor.get_productos(estado_filtro)
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudieron cargar los productos: {e}")
            productos = []

        # --- Filas de Datos ---
        if not productos:
            customtkinter.CTkLabel(self.productos_tabla_frame, text="No se encontraron productos con este filtro.", text_color="gray").grid(row=0, column=0, columnspan=6, padx=10, pady=20)
            return

        PAD_UNIFORME_Y = 5 
        last_widget_row = 0

        # Para simular la data de productos (DEBES OBTENER ESTO DE TU API REAL)
        # Nota: El servidor DEBE devolver los campos: id, nombre, estado, precio, stock, categoria.
        
        for row, data in enumerate(productos):
            row_index = row 
            producto_id = data.get("id", row + 1)
            
            # Formato de moneda (simple)
            try:
                # Convertimos explícitamente el valor de 'precio' a float ANTES de formatearlo
                precio_float = float(data.get('precio', 0.00))
                precio_str = f"${precio_float:.2f}"
            except ValueError:
                precio_str = "N/A" # En caso de que la cadena no sea un número válido

            # Repetimos la conversión para stock para asegurar que sea un entero
            try:
                stock_val = int(data.get("stock", 0))
                stock_str = str(stock_val)
            except ValueError:
                stock_val = 0
                stock_str = "0"

            items = [
                data.get("nombre", "N/A"), 
                data.get("estado", "N/A"), 
                precio_str, 
                str(data.get("stock", 0)),
                data.get("categoria", "N/A")
            ]

            # 1. Nombre (Col 0)
            customtkinter.CTkLabel(self.productos_tabla_frame, text=items[0]).grid(row=row_index, column=0, padx=10, pady=PAD_UNIFORME_Y, sticky="w")

            # 2. Estado (Col 1)
            # Para los estados que indican que está listo, usamos un color verde (ej: Listo para distribución)
            estado = items[1]
            if estado in ["Listo para distribución", "Disponible"]:
                color = "#008000"     # Verde (Listo/Disponible)
            elif estado == "En revisión de calidad":
                color = "#800080"     # Púrpura/Violeta (Revisión)
            elif estado == "En embalaje":
                color = "#E6A23C"     # Dorado/Naranja (Embalaje)
            elif estado == "Agotado":
                color = "#990000"     # Rojo Oscuro (Agotado/Crítico)
            else:
                color = "gray"        # Gris (Otros estados)
            
            customtkinter.CTkLabel(self.productos_tabla_frame, 
                                   text=estado, 
                                   text_color=color, 
                                   font=customtkinter.CTkFont(weight="bold")).grid(row=row_index, column=1, padx=10, pady=PAD_UNIFORME_Y, sticky="w")

            # 3. Precio (Col 2)
            customtkinter.CTkLabel(self.productos_tabla_frame, text=items[2]).grid(row=row_index, column=2, padx=10, pady=PAD_UNIFORME_Y, sticky="w")

            # 4. Stock (Col 3) - Se asume que el stock es un número
            stock_val = int(data.get("stock", 0))
            stock_color = "red" if stock_val < 10 else "black"
            customtkinter.CTkLabel(self.productos_tabla_frame, text=items[3], text_color=stock_color).grid(row=row_index, column=3, padx=10, pady=PAD_UNIFORME_Y, sticky="w")

            # 5. Categoría (Col 4)
            customtkinter.CTkLabel(self.productos_tabla_frame, text=items[4]).grid(row=row_index, column=4, padx=10, pady=PAD_UNIFORME_Y, sticky="w")
            
            # 6. Columna Acciones (Botón Vender) (Columna 5)
            vender_btn = customtkinter.CTkButton(
                self.productos_tabla_frame,
                text="Vender",
                command=lambda id=producto_id, name=items[0]: self._open_vender_producto_modal(id, name),
                width=80,
                fg_color=CELESTE_COLOR,
                hover_color="#3c6f9e", # Un azul más oscuro
                state="normal" if stock_val > 0 else "disabled" # Deshabilitar si no hay stock
            )
            vender_btn.grid(row=row_index, column=5, padx=10, pady=PAD_UNIFORME_Y, sticky="w")
            
            last_widget_row = row_index


        # 🚀 Fila fantasma con peso 1 para forzar la expansión vertical (COMO EN RRHH)
        fila_fantasma_index = last_widget_row + 1 if productos else 1
        self.productos_tabla_frame.grid_rowconfigure(fila_fantasma_index, weight=1)
        customtkinter.CTkLabel(self.productos_tabla_frame, text="", height=0, fg_color="transparent").grid(
            row=fila_fantasma_index,
            column=0,
            sticky="nsew"
        )


    def _filtrar_productos_tabla(self, estado_seleccionado):
        """Función que se llama al cambiar el filtro."""
        self._load_productos_data(estado_seleccionado)


    def _open_agregar_producto_modal(self):
        """Abre la ventana modal (Toplevel) para añadir un nuevo producto."""
        # Se implementará en la siguiente iteración
        messagebox.showinfo("Pendiente", "Se abrirá el modal para agregar un nuevo producto.")
        # modal = AgregarProductoModal(self)
        # modal.grab_set()
        
    def _open_vender_producto_modal(self, producto_id, nombre_producto):
        """Abre la ventana modal (Toplevel) para registrar una venta."""
        # Se implementará en la siguiente iteración
        messagebox.showinfo("Pendiente", f"Se abrirá el modal para registrar la venta de: {nombre_producto}.")
        # modal = RegistrarVentaModal(self, producto_id, nombre_producto)
        # modal.grab_set()


    # -----------------------------------------------------------------
    # VISTA 2: PANEL DE RENDIMIENTO (Placeholder)
    # -----------------------------------------------------------------

    def _show_rendimiento_view(self):
        self._clear_main_content()
        customtkinter.CTkLabel(self.main_content, text="Panel de Rendimiento (WIP)", font=customtkinter.CTkFont(size=20, weight="bold")).pack(padx=50, pady=50)


    # -----------------------------------------------------------------
    # VISTA 3: GESTIÓN DE CAMPAÑAS (Placeholder)
    # -----------------------------------------------------------------

    def _show_campañas_view(self):
        self._clear_main_content()
        customtkinter.CTkLabel(self.main_content, text="Gestión de Campañas (WIP)", font=customtkinter.CTkFont(size=20, weight="bold")).pack(padx=50, pady=50)


    # -----------------------------------------------------------------
    # VISTA 4: HISTORIAL DE VENTAS (Placeholder)
    # -----------------------------------------------------------------

    def _show_historial_view(self):
        self._clear_main_content()
        customtkinter.CTkLabel(self.main_content, text="Historial de Ventas (WIP)", font=customtkinter.CTkFont(size=20, weight="bold")).pack(padx=50, pady=50)

# --- Fin de VentasModule ---
