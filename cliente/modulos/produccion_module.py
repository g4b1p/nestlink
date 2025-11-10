import customtkinter
from tkinter import messagebox
import os
from PIL import Image
import re 
from datetime import datetime

# Importamos las dependencias clave
import conexion_servidor 

# Importación de la clase base y los colores
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

# =================================================================
# CLASE ESPECÍFICA PARA PRODUCCIÓN
# =================================================================

class ProduccionModule(BaseAppWindow):
    """Módulo de Producción."""
    
    MODULE_HEADER_ICON = ICON_MODULO_PRODUCCION

    # Asignación de íconos locales para el sidebar
    ICON_PRODUCTOS = ICON_PRODUCTOS 
    ICON_HISTORIAL = ICON_HISTORIAL_VENTAS

    def __init__(self, master, user_info):
        super().__init__(master, "Producción", user_info)
        
        user_id_from_info = user_info.get('user_id')
        self.user_id_logueado = user_id_from_info
        
        # 1. Configuración de botones laterales
        self.button_config = [
            ("Gestión de Productos", self._show_productos_view, self.ICON_PRODUCTOS),
            ("Historial de Ventas", self._show_historial_ventas_view, self.ICON_HISTORIAL),
        ]
        
        # 2. Configurar y mostrar los botones
        self._set_sidebar_buttons(self.button_config)
        
        # 3. Mostrar la vista inicial por defecto
        if self.button_config:
            self.active_view = self.button_config[0][0]
            self.button_config[0][1]()


    # =================================================================
    # VISTA 1: GESTIÓN DE PRODUCTOS (Creación y Edición)
    # =================================================================

    def _show_productos_view(self):
        """Muestra la interfaz para el listado, creación y edición de productos."""
        self._clear_main_content()

        # Configuración de expansión (Fila 1 para la tabla, se expande)
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # --- 1. Header de la Vista (Título, Filtro y Botón Agregar) ---
        view_header_frame = customtkinter.CTkFrame(self.main_content, fg_color="transparent")
        view_header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        view_header_frame.grid_columnconfigure(0, weight=1) 
        view_header_frame.grid_columnconfigure(1, weight=0) 
        view_header_frame.grid_columnconfigure(2, weight=0) # Para el botón

        customtkinter.CTkLabel(
            view_header_frame,
            text="Gestión de Productos",
            font=customtkinter.CTkFont(size=20, weight="bold"), 
            text_color="#5b94c6" 
        ).grid(row=0, column=0, sticky="w")

        # Filtro de Estado (CTkOptionMenu)
        estados = ["Todos los estados", "Listo para distribución", "En revisión de calidad", "En embalaje", "Materia Prima"]
        self.productos_filtro = customtkinter.CTkOptionMenu(
            view_header_frame,
            values=estados,
            command=self._filtrar_productos_tabla,
            width=220 
        )
        self.productos_filtro.grid(row=0, column=1, padx=(0, 20), sticky="e")
        
        # Botón "+ Agregar Producto" (ACTIVO para Producción)
        customtkinter.CTkButton(
            view_header_frame,
            text="+ Agregar Producto",
            command=self._open_agregar_producto_modal, # 🚨 ACTIVO
            fg_color="#00bf63", # Color verde para crear
            hover_color="#00994f",
            height=35,
            anchor="center"
        ).grid(row=0, column=2, sticky="e")

        # -----------------------------------------------------------------------
        # 2. Área de la Tabla
        # -----------------------------------------------------------------------

        self.table_border_container = customtkinter.CTkFrame(
            self.main_content,
            corner_radius=5,
            fg_color=MAIN_BG_COLOR,
            border_color=CELESTE_COLOR,
            border_width=2
        )
        self.table_border_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.table_border_container.grid_columnconfigure(0, weight=1)
        self.table_border_container.grid_rowconfigure(0, weight=0) # Cabecera fija
        self.table_border_container.grid_rowconfigure(1, weight=1) # Cuerpo scrollable

        # Definición de las columnas de la tabla de productos (CON columna "Acciones")
        self.productos_columnas = ["Nombre", "Estado", "Costo", "Stock", "Categoría", "Lote", "Acciones"]
        NUM_COLUMNAS_DATOS = len(self.productos_columnas)

        # PASO 2: Frame para la CABECERA FIJA
        self.header_fixed_frame = customtkinter.CTkFrame(
            self.table_border_container,
            fg_color=CELESTE_COLOR, 
            corner_radius=0
        )
        self.header_fixed_frame.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))

        # CLAVE A: COMPENSACIÓN SCROLLBAR
        self.header_fixed_frame.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17)

        # BUCLE DE CONFIGURACIÓN Y ETIQUETAS DEL ENCABEZADO
        # Pesos: Nombre (3), Estado(2), Costo(1), Stock(1), Categoría(2), Lote(1), Acciones(1)
        self.productos_column_weights = [3, 2, 1, 1, 2, 1, 1] 

        for i, col_name in enumerate(self.productos_columnas):
            self.header_fixed_frame.grid_columnconfigure(i, weight=self.productos_column_weights[i])
            customtkinter.CTkLabel(
                self.header_fixed_frame,
                text=col_name,
                font=customtkinter.CTkFont(weight="bold", size=13),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")


        # PASO 3: CTkScrollableFrame (la tabla de datos) 
        self.productos_tabla_frame = customtkinter.CTkScrollableFrame(
            self.table_border_container,
            fg_color="transparent"
        )
        self.productos_tabla_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))

        # Configuramos las columnas del cuerpo para que coincidan con la cabecera.
        for i in range(NUM_COLUMNAS_DATOS):
            self.productos_tabla_frame.grid_columnconfigure(i, weight=self.productos_column_weights[i])

        # Finalmente, cargamos los datos
        self._load_productos_data(estado_filtro=self.productos_filtro.get())


    def _load_productos_data(self, estado_filtro):
        """Carga datos del servidor (BD) y construye las filas de datos de productos (CON acciones)."""
        for widget in self.productos_tabla_frame.winfo_children():
            widget.destroy()

        # --- Obtención de Datos DEL SERVIDOR ---
        try:
            productos = conexion_servidor.get_productos(estado_filtro)
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudieron cargar los productos: {e}")
            productos = []

        # --- Filas de Datos ---
        if not productos:
            customtkinter.CTkLabel(self.productos_tabla_frame, text="No se encontraron productos con este filtro.", text_color="gray").grid(row=0, column=0, columnspan=len(self.productos_columnas), padx=10, pady=20)
            return

        PAD_UNIFORME_Y = 5 
        last_widget_row = 0

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
                data.get("categoria", "N/A"),
                data.get("lote", "N/A")
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
            
            # 6. 🚨 NUEVO: Lote (Col 5)
            customtkinter.CTkLabel(self.productos_tabla_frame, text=items[5]).grid(row=row_index, column=5, padx=10, pady=PAD_UNIFORME_Y, sticky="w")

            # 1. Creamos el Frame contenedor para los botones
            actions_frame = customtkinter.CTkFrame(self.productos_tabla_frame, fg_color="transparent")
            # 🚨 Colocamos el frame CONTENEDOR en la COLUMNA 5 de la TABLA PRINCIPAL
            actions_frame.grid(row=row_index, column=6, padx=10, pady=PAD_UNIFORME_Y, sticky="w")

            stock_val = int(data.get("stock", 0))

            # 2. Botón EDITAR (Celeste/Azul)
            editar_btn = customtkinter.CTkButton(
                actions_frame, # <-- IMPORTANTE: Lo colocamos en actions_frame
                text="Editar",
                command=lambda id=producto_id, data=data: self._open_editar_producto_modal(id, data),
                width=75,
                fg_color=CELESTE_COLOR, 
                hover_color="#3c6f9e"
            )
            editar_btn.grid(row=0, column=0, padx=(0, 5), sticky="w") # Posición dentro de actions_frame
            
            # Botón VENDER (MODIFICADO)
            vender_btn = customtkinter.CTkButton(
                actions_frame,
                text="Vender",
                # 🚨 Asegúrate que la llamada envía los 4 argumentos (Python añade 'self' como 5to)
                command=lambda id=producto_id, name=data.get("nombre", "N/A"), stock=stock_val: self._open_vender_producto_modal(id, name, stock, self.user_id_logueado),
                width=75,
                fg_color="#555555", 
                hover_color="#444444", 
                state="normal" if stock_val > 0 else "disabled"
            )
            vender_btn.grid(row=0, column=1, padx=(5, 0), sticky="w")
            
            last_widget_row = row_index


        # Fila fantasma con peso 1 para forzar la expansión vertical
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
        """Abre el modal para crear un nuevo producto (incluye Materia Prima)."""
        modal = AgregarProductoModal(self.master, self._load_productos_data)
        modal.grab_set()

    def _open_editar_producto_modal(self, producto_id, producto_data):
        """Abre el modal para editar un producto existente."""
        modal = EditarProductoModal(self.master, producto_id, producto_data, self._show_productos_view)

    def _open_vender_producto_modal(self, producto_id, nombre_producto, stock_actual, id_vendedor):
            # 🚨 SOLUCIÓN: La cabecera ahora acepta 5 argumentos, incluyendo 'id_vendedor'.
        """Abre la ventana modal (Toplevel) para registrar una venta."""
        messagebox.showinfo("Acceso Denegado", "No tienes permiso para vender productos. Esta función está reservada para el sector de Ventas.")

    # =================================================================
    # VISTA 2: HISTORIAL DE VENTAS (Análisis de Planificación)
    # =================================================================

    def _show_historial_ventas_view(self):
        """Muestra la vista de historial de ventas con la estética para análisis de Producción."""
        self._clear_main_content() 

        # Configuración de expansión 
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # --- 1. Header de la Vista (Título y Filtro) ---
        view_header_frame = customtkinter.CTkFrame(self.main_content, fg_color="transparent")
        view_header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        view_header_frame.grid_columnconfigure(0, weight=1) 
        view_header_frame.grid_columnconfigure(1, weight=0) 

        customtkinter.CTkLabel(
            view_header_frame,
            text="Historial de Ventas",
            font=customtkinter.CTkFont(size=20, weight="bold"), 
            text_color="#5b94c6" 
        ).grid(row=0, column=0, sticky="w")
        
        # Frame del Filtro (derecha)
        filtro_frame = customtkinter.CTkFrame(view_header_frame, fg_color="transparent")
        filtro_frame.grid(row=0, column=1, sticky="e")
        
        customtkinter.CTkLabel(filtro_frame, text="Filtrar por Categoría:").grid(row=0, column=0, padx=(0, 5), sticky="w")

        # OptionMenu para Categorías
        self.ventas_categoria_filtro = customtkinter.CTkOptionMenu(
            filtro_frame,
            values=["Cargando..."],
            command=self._filter_ventas_table 
        )
        self.ventas_categoria_filtro.grid(row=0, column=1, sticky="e")

        # -----------------------------------------------------------------------
        # 2. Área de la Tabla
        # -----------------------------------------------------------------------

        self.table_border_container_ventas = customtkinter.CTkFrame(
            self.main_content,
            corner_radius=5,
            fg_color=MAIN_BG_COLOR,
            border_color=CELESTE_COLOR,
            border_width=2
        )
        self.table_border_container_ventas.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.table_border_container_ventas.grid_columnconfigure(0, weight=1)
        self.table_border_container_ventas.grid_rowconfigure(0, weight=0) 
        self.table_border_container_ventas.grid_rowconfigure(1, weight=1) 

        self.ventas_columnas = ["Producto", "Categoría", "Cantidad", "Fecha Venta", "Cliente", "Vendedor", "Monto Total"]
        NUM_COLUMNAS_DATOS = len(self.ventas_columnas)
        self.ventas_column_weights = [2, 1, 1, 2, 2, 2, 1] 

        self.header_fixed_frame_ventas = customtkinter.CTkFrame(
            self.table_border_container_ventas,
            fg_color=CELESTE_COLOR, 
            corner_radius=0
        )
        self.header_fixed_frame_ventas.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))

        self.header_fixed_frame_ventas.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17) 

        for i, col_name in enumerate(self.ventas_columnas):
            self.header_fixed_frame_ventas.grid_columnconfigure(i, weight=self.ventas_column_weights[i])
            customtkinter.CTkLabel(
                self.header_fixed_frame_ventas,
                text=col_name,
                font=customtkinter.CTkFont(weight="bold", size=13),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        self.ventas_tabla_frame = customtkinter.CTkScrollableFrame(
            self.table_border_container_ventas,
            fg_color="transparent" 
        )
        self.ventas_tabla_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))

        for i in range(NUM_COLUMNAS_DATOS):
            self.ventas_tabla_frame.grid_columnconfigure(i, weight=self.ventas_column_weights[i])

        self._populate_ventas_filters()
        self._load_ventas_data()

    def _populate_ventas_filters(self):
        """Carga las categorías disponibles para el filtro."""
        try:
            categorias = conexion_servidor.get_categorias_ventas()
            # Añadir la opción 'Todas' al principio
            opciones = ["Todas"] + sorted(categorias)
            self.ventas_categoria_filtro.configure(values=opciones)
            self.ventas_categoria_filtro.set("Todas")
        except Exception as e:
            print(f"Error al poblar filtros de ventas: {e}")
            self.ventas_categoria_filtro.configure(values=["Error"])
            self.ventas_categoria_filtro.set("Error")

    def _filter_ventas_table(self, selected_category):
        """Se llama cuando se selecciona una categoría en el OptionMenu."""
        self._load_ventas_data(selected_category)

    def _load_ventas_data(self, categoria_filtro=None):
        """Carga datos de ventas del servidor y construye las filas."""
        for widget in self.ventas_tabla_frame.winfo_children():
            widget.destroy()

        try:
            historial_ventas = conexion_servidor.get_historial_ventas(categoria_filtro)
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar el historial de ventas: {e}")
            historial_ventas = []

        if not historial_ventas:
            customtkinter.CTkLabel(
                self.ventas_tabla_frame, 
                text="No se encontraron ventas con este filtro.", 
                text_color="gray"
            ).grid(row=0, column=0, columnspan=len(self.ventas_columnas), padx=10, pady=20)
            return

        PAD_Y = 5
        last_widget_row = 0
        
        for row, data in enumerate(historial_ventas):
            row_index = row
            
            try:
                monto_str = f"${float(data.get('monto_total', 0.00)):,.2f}"
            except ValueError:
                monto_str = "N/A"

            row_data = [
                data.get("nombre_producto", "N/A"),
                data.get("categoria", "N/A"),
                data.get("cantidad", 0),
                data.get("fecha_venta", "N/A"),
                monto_str,
                data.get("nombre_vendedor", "N/A")
            ]

            for col, value in enumerate(row_data):
                customtkinter.CTkLabel(
                    self.ventas_tabla_frame, 
                    text=str(value), 
                    anchor="w", 
                    text_color="black", 
                    fg_color="transparent"
                ).grid(row=row_index, column=col, padx=10, pady=PAD_Y, sticky="w")
            
            last_widget_row = row_index

        fila_fantasma_index = last_widget_row + 1 if historial_ventas else 1
        self.ventas_tabla_frame.grid_rowconfigure(fila_fantasma_index, weight=1)
        customtkinter.CTkLabel(self.ventas_tabla_frame, text="", height=0, fg_color="transparent").grid(
            row=fila_fantasma_index,
            column=0,
            sticky="nsew"
        )


class AgregarProductoModal(customtkinter.CTkToplevel):
    def __init__(self, master, callback_reload):
        super().__init__(master)
        self.title("Agregar Nuevo Producto")
        self.geometry("500x550")
        self.transient(master) # Mantener el modal encima de la ventana principal
        self.grab_set()        # Bloquear interacción con otras ventanas
        
        self.callback_reload = callback_reload # Función para recargar la tabla principal

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Colores deben estar definidos en tu archivo (ej: SIDEBAR_COLOR)
        # Si no lo tienes, usa un color como "gray10"
        
        main_frame = customtkinter.CTkFrame(self, fg_color=SIDEBAR_COLOR, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        
        self._create_widgets(main_frame)

    def _create_widgets(self, main_frame):
        # Título
        customtkinter.CTkLabel(main_frame, text="REGISTRAR NUEVO PRODUCTO", 
                               font=customtkinter.CTkFont(size=18, weight="bold"),
                               text_color="white").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # Frame contenedor para inputs
        form_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        row_num = 0

        # Campo 1: Nombre
        customtkinter.CTkLabel(form_frame, text="Nombre:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_nombre = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_nombre.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 2: Categoría
        customtkinter.CTkLabel(form_frame, text="Categoría:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        CATEGORIAS_OPTIONS = ["Chocolates", "Alimentos", "Bebidas", "Lácteos"]
        self.option_categoria_var = customtkinter.StringVar(value=CATEGORIAS_OPTIONS[0])
    
        self.option_categoria = customtkinter.CTkOptionMenu(
            form_frame, 
            values=CATEGORIAS_OPTIONS, 
            variable=self.option_categoria_var, # Vincula el OptionMenu a la variable
            width=200
        )
        self.option_categoria.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1

        # Campo 3: Precio
        customtkinter.CTkLabel(form_frame, text="Precio Unitario:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_precio = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_precio.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 4: Stock
        customtkinter.CTkLabel(form_frame, text="Stock Inicial:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_stock = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_stock.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 5: Estado (OptionMenu)
        customtkinter.CTkLabel(form_frame, text="Estado:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        estados_posibles = ["Listo para distribución", "En revisión de calidad", "En embalaje", "Agotado"]
        self.option_estado = customtkinter.CTkOptionMenu(form_frame, values=estados_posibles, width=200)
        self.option_estado.set(estados_posibles[0]) # Estado por defecto
        self.option_estado.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 6: Lote
        customtkinter.CTkLabel(form_frame, text="Lote:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_lote = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_lote.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1

        # Mensaje de error/éxito
        self.message_label = customtkinter.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Frame de botones
        btn_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        # Botón Guardar
        customtkinter.CTkButton(
            btn_frame, 
            text="Registrar Producto", 
            command=self._save_new_product,
            fg_color="#00bf63", # Verde
            hover_color="#00994f"
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Botón Cancelar
        customtkinter.CTkButton(
            btn_frame, 
            text="Cancelar", 
            command=self.destroy,
            fg_color="#B22222", 
            hover_color="#8B0000"
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")


    def _save_new_product(self):
        """Valida los datos y envía la solicitud POST al servidor."""
        nombre = self.entry_nombre.get()
        categoria = self.entry_categoria.get()
        precio_raw = self.entry_precio.get().replace(',', '.')
        stock_raw = self.entry_stock.get()
        lote = self.entry_lote.get()
        estado = self.option_estado.get()

        # Validación de campos vacíos
        if not nombre or not categoria or not precio_raw or not stock_raw or not lote:
            self.message_label.configure(text="Todos los campos son obligatorios.")
            return

        # Validación de Precio
        try:
            precio = float(precio_raw)
            if precio <= 0: raise ValueError
        except ValueError:
            self.message_label.configure(text="El precio debe ser un número positivo (ej: 19.99).")
            return

        # Validación de Stock
        try:
            stock = int(stock_raw)
            if stock < 0: raise ValueError
        except ValueError:
            self.message_label.configure(text="El stock debe ser un número entero no negativo.")
            return

        # Preparar los datos para enviar al servidor
        new_product_data = {
            "nombre": nombre, 
            "categoria": categoria,
            "precio_unitario": precio, 
            "stock": stock,
            "estado": estado,
            "lote": lote
        }

        # Lógica de conexión (POST)
        try:
            # 🚨 NOTA: Llama a la nueva función de conexión que crearemos en el siguiente paso
            success, message = conexion_servidor.create_producto(new_product_data)
            
            if success:
                messagebox.showinfo("Éxito", message)
                self.callback_reload() # Recargar la tabla principal
                self.destroy()
            else:
                self.message_label.configure(text=f"Error al registrar: {message}", text_color="red")

        except Exception as e:
            self.message_label.configure(text=f"Error de conexión: {e}", text_color="red")


class EditarProductoModal(customtkinter.CTkToplevel):
    def __init__(self, master, producto_id, producto_data, callback_reload):
        super().__init__(master)
        self.title(f"Editar Producto: {producto_data['nombre']}")
        self.geometry("500x550")
        self.transient(master) # Mantener el modal encima de la ventana principal
        self.grab_set()        # Bloquear interacción con otras ventanas
        
        self.producto_id = producto_id
        self.producto_data = producto_data
        self.callback_reload = callback_reload # Función para recargar la tabla principal

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = customtkinter.CTkFrame(self, fg_color=SIDEBAR_COLOR, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        
        self._create_widgets(main_frame)

    def _create_widgets(self, main_frame):
        # Título
        customtkinter.CTkLabel(main_frame, text="MODIFICAR DATOS DEL PRODUCTO", 
                               font=customtkinter.CTkFont(size=18, weight="bold"),
                               text_color="white").grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="n")

        # Frame contenedor para inputs
        form_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        row_num = 0

        # Campo 1: Nombre (Solo lectura, ya que el ID no se debe cambiar)
        customtkinter.CTkLabel(form_frame, text="Nombre:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_nombre = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_nombre.insert(0, self.producto_data['nombre'])
        self.entry_nombre.configure(state="disabled", text_color="gray") # Deshabilitar edición
        self.entry_nombre.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 2: Categoría (Solo lectura)
        customtkinter.CTkLabel(form_frame, text="Categoría:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_categoria = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_categoria.insert(0, self.producto_data['categoria'])
        self.entry_categoria.configure(state="disabled", text_color="gray") # Deshabilitar edición
        self.entry_categoria.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1

        # Campo 3: Precio
        customtkinter.CTkLabel(form_frame, text="Precio Unitario:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_precio = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_precio.insert(0, str(float(self.producto_data.get('precio', 0.00)))) # Usamos float para evitar el $
        self.entry_precio.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 4: Stock
        customtkinter.CTkLabel(form_frame, text="Stock:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_stock = customtkinter.CTkEntry(form_frame, width=200)
        self.entry_stock.insert(0, str(self.producto_data['stock']))
        self.entry_stock.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 5: Estado (OptionMenu)
        customtkinter.CTkLabel(form_frame, text="Estado:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        estados_posibles = ["Listo para distribución", "En revisión de calidad", "En embalaje"]
        self.option_estado = customtkinter.CTkOptionMenu(form_frame, values=estados_posibles, width=200)
        self.option_estado.set(self.producto_data['estado'])
        self.option_estado.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1
        
        # Campo 6: Lote
        customtkinter.CTkLabel(form_frame, text="Lote:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(15, 2), sticky="w")
        self.entry_lote = customtkinter.CTkEntry(form_frame, width=200)
        # Asumimos que 'lote' es un campo que puede venir en los datos
        self.entry_lote.insert(0, self.producto_data.get('lote', ''))
        self.entry_lote.grid(row=row_num, column=1, padx=10, pady=(15, 2), sticky="ew")
        row_num += 1

        # Mensaje de error/éxito
        self.message_label = customtkinter.CTkLabel(main_frame, text="", text_color="red")
        self.message_label.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Frame de botones
        btn_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        # Botón Guardar
        customtkinter.CTkButton(
            btn_frame, 
            text="Guardar Cambios", 
            command=self._save_changes,
            fg_color="#00bf63", # Verde
            hover_color="#00994f"
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Botón Cancelar
        customtkinter.CTkButton(
            btn_frame, 
            text="Cancelar", 
            command=self.destroy,
            fg_color="#B22222", 
            hover_color="#8B0000"
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")


    def _save_changes(self):
        """Valida los datos y envía la solicitud PUT al servidor."""
        precio_raw = self.entry_precio.get().replace(',', '.')
        stock_raw = self.entry_stock.get()
        lote = self.entry_lote.get()
        estado = self.option_estado.get()

        # Validación
        if not precio_raw or not stock_raw or not lote:
            self.message_label.configure(text="Todos los campos editables son obligatorios.")
            return

        try:
            precio = float(precio_raw)
            if precio <= 0: raise ValueError
        except ValueError:
            self.message_label.configure(text="El precio debe ser un número positivo.")
            return

        try:
            stock = int(stock_raw)
            if stock < 0: raise ValueError
        except ValueError:
            self.message_label.configure(text="El stock debe ser un número entero no negativo.")
            return

        # Preparar los datos para enviar al servidor
        update_data = {
            "precio_unitario": precio, # Usamos el nombre de la columna de la BD (app.py lo espera)
            "stock": stock,
            "estado": estado,
            "lote": lote
        }

        # Lógica de conexión (PUT)
        try:
            success, message = conexion_servidor.update_producto(self.producto_id, update_data)
            
            if success:
                messagebox.showinfo("Éxito", message)
                self.callback_reload() # Recargar la tabla principal
                self.destroy()
            else:
                self.message_label.configure(text=f"Error al actualizar: {message}", text_color="red")

        except Exception as e:
            self.message_label.configure(text=f"Error de conexión: {e}", text_color="red")