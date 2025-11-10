import customtkinter
from tkinter import messagebox
import os
from PIL import Image
from datetime import datetime, timedelta  # <--- ¡ESTO ES LO QUE FALTABA!
import calendar

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

TIPOS_MOVIMIENTO = ["ENTRADA", "SALIDA", "AJUSTE"]

class LogisticaModule(BaseAppWindow):
    """Módulo de Logística."""
    
    MODULE_HEADER_ICON = ICON_MODULO_LOGISTICA

    def __init__(self, master, user_info):
        super().__init__(master, "Logística", user_info)
        
        now = datetime.now()
        self.current_date = datetime(now.year, now.month, 1) 
        self.current_month = self.current_date.month
        self.current_year = self.current_date.year
        self.movimientos_del_mes = {}
        
        user_id_from_info = user_info.get('user_id')
        self.user_id_logueado = user_id_from_info
        
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
        
        self.active_view = self.button_config[0][0]
        
        self.productos_list = []
        self._load_simple_productos_for_modal() # Cargar los datos al inicio

    def _load_simple_productos_for_modal(self): 
        """Carga la lista de productos (ID y Nombre) desde el servidor para el selector del modal."""
        # 🚨 ASEGÚRATE QUE TODO ESTE BLOQUE ESTÉ CORRECTAMENTE INDENTADO (4 espacios o 1 tab)
        try:
            data = conexion_servidor.get_productos_list() 
            
            # Verificamos que 'data' sea una lista (la respuesta del servidor)
            if isinstance(data, list):
                self.productos_list = data
            else:
                print(f"Advertencia: Respuesta de productos no es una lista esperada: {data}")
                self.productos_list = []
                
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar los productos: {e}")
            self.productos_list = []

    # =================================================================
    # VISTAS
    # =================================================================

    def _show_productos_view(self):
        """Muestra la interfaz para el listado de productos (solo vista)."""
        self._clear_main_content()

        # Configuración de expansión (Fila 1 para la tabla, se expande)
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # --- 1. Header de la Vista (Título y Filtro) ---
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
        estados = ["Todos los estados", "Listo para distribución", "En revisión de calidad", "En embalaje"]
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
            fg_color="#555555",
            hover_color="#444444",
            height=35,
            anchor="center"
        ).grid(row=0, column=2, sticky="e")

        # -----------------------------------------------------------------------
        # 2. Área de la Tabla (Contenedor con Borde, Cabecera FIJA y ScrollableFrame)
        # -----------------------------------------------------------------------

        # PASO 1: Contenedor que maneja el Borde
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

        # Definición de las columnas de la tabla de productos (SIN columna "Acciones")
        columnas = ["Nombre", "Estado", "Precio", "Stock", "Categoría", "Lote", "Acciones"]
        NUM_COLUMNAS_DATOS = len(columnas)

        # 🚨 PASO 2: Frame para la CABECERA FIJA
        self.header_fixed_frame = customtkinter.CTkFrame(
            self.table_border_container,
            fg_color="#5b94c6", # Color Azul de la Cabecera
            corner_radius=0
        )
        self.header_fixed_frame.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))

        # CLAVE A: COMPENSACIÓN SCROLLBAR
        self.header_fixed_frame.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17)

        # BUCLE DE CONFIGURACIÓN Y ETIQUETAS DEL ENCABEZADO
        # Nombre, Categoría más peso. Precio, Stock, Lote menos.
        column_weights = [3, 2, 1, 1, 2, 1, 0]

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
        """Carga datos del servidor (BD) y construye las filas de datos de productos (sin acciones)."""
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
                fg_color="#555555",
                hover_color="#444444"
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
        """Abre la ventana modal (Toplevel) para agregar un nuevo producto."""
        # 🚨 NOTA: Pasamos la función de recarga de datos de la tabla principal.
        #modal = AgregarProductoModal(self.master, self._show_productos_view)
        messagebox.showinfo("Acceso Denegado", "No tienes permiso para agregar productos. Esta función está reservada para el sector de Producción.")

    def _open_vender_producto_modal(self, producto_id, nombre_producto, stock_actual, id_vendedor):
            # 🚨 SOLUCIÓN: La cabecera ahora acepta 5 argumentos, incluyendo 'id_vendedor'.
        """Abre la ventana modal (Toplevel) para registrar una venta."""
        messagebox.showinfo("Acceso Denegado", "No tienes permiso para vender productos. Esta función está reservada para el sector de Ventas.")

    
    def _open_editar_producto_modal(self, producto_id, producto_data):
        """Abre la ventana modal (Toplevel) para editar un producto existente."""
        
        # 🚨 NOTA: Pasamos la función de recarga de datos de la tabla principal.
        #modal = EditarProductoModal(self.master, producto_id, producto_data, self._show_productos_view) 
        # El _show_productos_view recarga la tabla y vuelve a dibujar toda la vista.
        messagebox.showinfo("Acceso Denegado", "No tienes permiso para editar productos. Esta función está reservada para el sector de Producción.")


    def _show_calendario_view(self):
        self._clear_main_content()
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1) # Dos columnas para Calendario y Lista

        # --- Columna 0: El Calendario (70%) ---
        calendar_col = customtkinter.CTkFrame(self.main_content, fg_color="transparent")
        calendar_col.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=20, pady=20)
        calendar_col.grid_columnconfigure(0, weight=1)
        calendar_col.grid_rowconfigure(0, weight=0)
        calendar_col.grid_rowconfigure(1, weight=1)

        # 1. Header del Calendario (Navegación)
        nav_frame = customtkinter.CTkFrame(calendar_col, fg_color=SIDEBAR_COLOR)
        nav_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        nav_frame.grid_columnconfigure(1, weight=1)

        # Botón Anterior
        customtkinter.CTkButton(nav_frame, text="<", width=50, command=lambda: self._change_month(-1)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Título del Mes
        self.month_label = customtkinter.CTkLabel(nav_frame, text="", font=customtkinter.CTkFont(size=20, weight="bold"), text_color="white")
        self.month_label.grid(row=0, column=1, padx=10, pady=10)

        # Botón Siguiente
        customtkinter.CTkButton(nav_frame, text=">", width=50, command=lambda: self._change_month(1)).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # 2. Grid del Calendario
        self.calendar_grid_frame = customtkinter.CTkFrame(calendar_col, fg_color=CONTENT_BG_COLOR, corner_radius=5)
        self.calendar_grid_frame.grid(row=1, column=0, sticky="nsew")

        # --- Columna 1: Detalle del Día Seleccionado (30%) ---
        details_col = customtkinter.CTkFrame(self.main_content, fg_color=CONTENT_BG_COLOR, corner_radius=5)
        details_col.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 20), pady=20)
        details_col.grid_columnconfigure(0, weight=1)
        details_col.grid_rowconfigure(2, weight=1)
        
        # Header de detalles
        self.details_header = customtkinter.CTkLabel(details_col, text="Selecciona un día", font=customtkinter.CTkFont(size=18, weight="bold"), text_color=CELESTE_COLOR)
        self.details_header.grid(row=0, column=0, padx=15, pady=(20, 10), sticky="w")
        
        # Botón para crear movimiento
        self.create_movement_btn = customtkinter.CTkButton(
            details_col,
            text="+ Nuevo Movimiento",
            command=self._open_agregar_movimiento_modal,
            fg_color="#00bf63", 
            hover_color="#00994f",
            state="disabled" # Deshabilitado hasta que se seleccione un día
        )
        self.create_movement_btn.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        # Scrollable Frame para la lista de movimientos
        self.movimientos_list_frame = customtkinter.CTkScrollableFrame(details_col, fg_color="transparent")
        self.movimientos_list_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.movimientos_list_frame.grid_columnconfigure(0, weight=1)

        # Mostrar calendario inicial
        self._draw_calendar()
    
    # -----------------------------------------------------------
    # Lógica de Calendario
    # -----------------------------------------------------------

    def _change_month(self, delta):
        """Avanza o retrocede el mes del calendario, manejando el cambio de año correctamente."""
        
        new_month = self.current_month + delta
        new_year = self.current_year

        # Manejar el salto de año hacia adelante
        if new_month > 12:
            new_month -= 12
            new_year += 1
        # Manejar el salto de año hacia atrás
        elif new_month < 1:
            new_month += 12
            new_year -= 1

        # Almacenamos la nueva fecha como el primer día del mes.
        # Esto garantiza que siempre es una fecha válida (p. ej., no hay 31 de Febrero)
        try:
            self.current_date = datetime(new_year, new_month, 1)
        except ValueError as e:
            # Esto es una medida de seguridad, aunque la lógica anterior debería prevenirlo
            messagebox.showerror("Error de Fecha", f"Error al configurar la fecha: {e}")
            return 
            
        self.current_month = new_month
        self.current_year = new_year
        self._draw_calendar()

    def _draw_calendar(self):
        """Dibuja la cuadrícula del calendario para el mes y año actuales."""
        
        # Limpiar cuadrícula
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        # Actualizar título
        month_name = calendar.month_name[self.current_month]
        self.month_label.configure(text=f"{month_name.upper()} {self.current_year}")

        # Intentar cargar movimientos del mes (asumiendo función de conexión)
        self._load_movimientos_del_mes() 
        
        # Días de la semana (Fila 0)
        weekdays = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for col, day in enumerate(weekdays):
            self.calendar_grid_frame.grid_columnconfigure(col, weight=1)
            customtkinter.CTkLabel(
                self.calendar_grid_frame, 
                text=day, 
                font=customtkinter.CTkFont(weight="bold"), 
                text_color=CELESTE_COLOR
            ).grid(row=0, column=col, padx=5, pady=10)

        # Generar días del mes
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_days = cal.monthdatescalendar(self.current_year, self.current_month)
        
        current_day_of_month = self.current_date.day

        for week_index, week in enumerate(month_days):
            for day_index, day_date in enumerate(week):
                row = week_index + 1
                col = day_index
                
                day_btn = customtkinter.CTkButton(
                    self.calendar_grid_frame, 
                    text=str(day_date.day),
                    width=40,
                    height=40,
                    fg_color=CONTENT_BG_COLOR if day_date.month == self.current_month else "gray50",
                    text_color="black",
                    hover_color="gray70",
                    command=lambda d=day_date: self._select_day(d)
                )
                
                # Resaltar día actual (AQUÍ ESTÁ LA CORRECCIÓN)
                # datetime.now() devuelve un datetime, al que SÍ hay que llamar .date()
                if day_date == datetime.now().date(): 
                    day_btn.configure(border_width=3, border_color="#e6b800")
                
                # Resaltar días con movimientos
                if day_date.day in self.movimientos_del_mes and day_date.month == self.current_month:
                    day_btn.configure(fg_color=CELESTE_COLOR, text_color="white", hover_color="#3c6f9e") 
                
                day_btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _load_movimientos_del_mes(self):
        """Carga movimientos del servidor para el mes y año actuales."""
        self.movimientos_del_mes = {} # Limpiar caché

        start_date = datetime(self.current_year, self.current_month, 1).strftime('%Y-%m-%d')
        # Calcular el último día del mes
        if self.current_month == 12:
            end_date = datetime(self.current_year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(self.current_year, self.current_month + 1, 1) - timedelta(days=1)
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        try:
            data = conexion_servidor.get_movimientos_rango(start_date, end_date_str)
            
            for movimiento in data:
                fecha_str_recibida = movimiento.get('fecha_movimiento')

                # 1. Validar si la fecha recibida es nula o inválida
                if not fecha_str_recibida or '0000-00-00' in fecha_str_recibida:
                    continue # Ignoramos este movimiento, no podemos agendarlo

                try:
                    # 2. Intentar analizar la fecha (formato YYYY-MM-DD HH:MM:SS)
                    # Tomamos solo la parte de la fecha (antes del espacio)
                    fecha_solo = fecha_str_recibida.split(' ')[0]
                    fecha = datetime.strptime(fecha_solo, '%Y-%m-%d')
                except ValueError:
                    # Si falla, imprimimos el error pero continuamos
                    print(f"Advertencia: Fecha inválida recibida del servidor: {fecha_str_recibida}")
                    continue

                # 3. Lógica de caché (sin cambios)
                day = fecha.day
                if day not in self.movimientos_del_mes:
                    self.movimientos_del_mes[day] = []
                self.movimientos_del_mes[day].append(movimiento)
                
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudieron cargar los movimientos: {e}")
            
    def _select_day(self, day_date):
        """Maneja la selección de un día en el calendario."""
        self.selected_day = day_date
        self.details_header.configure(text=day_date.strftime('%d de %B, %Y'))
        self.create_movement_btn.configure(state="normal")
        self._load_movimientos_del_day(day_date)

    def _load_movimientos_del_day(self, day_date):
        """Muestra la lista de movimientos para el día seleccionado."""
        for widget in self.movimientos_list_frame.winfo_children():
            widget.destroy()

        day = day_date.day
        movimientos = self.movimientos_del_mes.get(day, [])
        
        if not movimientos or day_date.month != self.current_month:
             customtkinter.CTkLabel(self.movimientos_list_frame, text="No hay movimientos agendados para este día.").grid(row=0, column=0, padx=10, pady=20)
             return

        for row, mov in enumerate(movimientos):
            # Tarjeta de Movimiento
            card = customtkinter.CTkFrame(self.movimientos_list_frame, fg_color="white", corner_radius=5)
            card.grid(row=row, column=0, sticky="ew", pady=5)
            card.grid_columnconfigure(0, weight=1)
            
            # --- 🚨 CORRECCIONES AQUÍ ---
            # Usamos 'tipo_movimiento' que SÍ viene de la BD
            tipo = mov.get('tipo_movimiento', 'Movimiento') 
            # 'estado' NO viene de la BD, así que lo quitamos del título
            producto_nombre = mov.get('nombre_producto', 'N/A')
            origen_destino = mov.get('origen_destino', 'N/A') # Obtenemos el origen/destino
            movimiento_id = mov.get('id_movimiento')
            
            # Definimos color basado en el tipo
            if tipo == "ENTRADA":
                color = "#00b33c" # Verde
            elif tipo == "SALIDA":
                color = "#ff6666" # Rojo
            else:
                color = "#E6A23C" # Naranja (Ajuste)

            # Título (Tipo y Producto)
            customtkinter.CTkLabel(
                card, 
                text=f"📦 {tipo}",  # Quitamos la referencia a (estado)
                font=customtkinter.CTkFont(weight="bold"), 
                text_color=color
            ).grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
            customtkinter.CTkLabel(card, text=f"Producto: {producto_nombre}", text_color="black").grid(row=1, column=0, padx=10, pady=(2, 5), sticky="w")
            
            # Botón de acción
            action_btn = customtkinter.CTkButton(
                card, 
                text="Ver/Editar", 
                command=lambda id=movimiento_id, data=mov: self._open_editar_movimiento_modal(id, data),
                width=80, 
                height=25,
                fg_color=CELESTE_COLOR
            )
            action_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="e")
            
        self.movimientos_list_frame.grid_rowconfigure(len(movimientos), weight=1) # Fila fantasma

    def _open_agregar_movimiento_modal(self):
        """Abre el modal en modo 'create'."""
        if self.selected_day:
            # Pasa la fecha seleccionada por el usuario como fecha por defecto
            default_date_str = self.selected_day.strftime('%Y-%m-%d')
            MovimientoModal(
                master=self, 
                callback_reload=self._draw_calendar, 
                default_date=default_date_str, 
                mode='create'
            )
        else:
            messagebox.showwarning("Selección Requerida", "Por favor, selecciona un día en el calendario primero.")

    def _open_editar_movimiento_modal(self, movimiento_id, data):
        """Abre el modal en modo 'edit' y precarga los datos."""
        MovimientoModal(
            master=self, 
            callback_reload=self._draw_calendar, 
            movimiento_id=movimiento_id, 
            data=data, 
            mode='edit'
        )
    
    

    def _show_historial_ventas_view(self):
        """Muestra la vista de historial de ventas con la estética de Gestión de Campañas/Productos."""
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

        # PASO 1: Contenedor que maneja el Borde
        self.table_border_container_ventas = customtkinter.CTkFrame(
            self.main_content,
            corner_radius=5,
            fg_color=MAIN_BG_COLOR,
            border_color="#5b94c6",
            border_width=2
        )
        self.table_border_container_ventas.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.table_border_container_ventas.grid_columnconfigure(0, weight=1)
        self.table_border_container_ventas.grid_rowconfigure(0, weight=0) # Cabecera fija
        self.table_border_container_ventas.grid_rowconfigure(1, weight=1) # Cuerpo scrollable

        # Definición de las columnas de la tabla de ventas
        self.ventas_columnas = ["Producto", "Categoría", "Cantidad", "Fecha Venta", "Cliente", "Vendedor", "Monto Total"]
        NUM_COLUMNAS_DATOS = len(self.ventas_columnas)
        self.ventas_column_weights = [2, 1, 1, 2, 2, 2, 1] 

        # PASO 2: Frame para la CABECERA FIJA
        self.header_fixed_frame_ventas = customtkinter.CTkFrame(
            self.table_border_container_ventas,
            fg_color=CELESTE_COLOR, 
            corner_radius=0
        )
        self.header_fixed_frame_ventas.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))

        self.header_fixed_frame_ventas.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17) # Scrollbar

        # BUCLE DE CONFIGURACIÓN Y ETIQUETAS DEL ENCABEZADO
        for i, col_name in enumerate(self.ventas_columnas):
            self.header_fixed_frame_ventas.grid_columnconfigure(i, weight=self.ventas_column_weights[i])
            customtkinter.CTkLabel(
                self.header_fixed_frame_ventas,
                text=col_name,
                font=customtkinter.CTkFont(weight="bold", size=13),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")


        # PASO 3: CTkScrollableFrame (la tabla de datos) 
        self.ventas_tabla_frame = customtkinter.CTkScrollableFrame(
            self.table_border_container_ventas,
            fg_color="transparent" 
        )
        self.ventas_tabla_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))

        for i in range(NUM_COLUMNAS_DATOS):
            self.ventas_tabla_frame.grid_columnconfigure(i, weight=self.ventas_column_weights[i])

        # Carga de datos de Historial de Ventas
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

    def _load_ventas_data(self, categoria_filtro="Todas"):
        """Carga datos de ventas del servidor y construye las filas con estética transparente y texto visible."""
        
        for widget in self.ventas_tabla_frame.winfo_children():
            widget.destroy() 

        try:
            filtro = categoria_filtro if categoria_filtro != 'Todas' else ""
            historial_ventas = conexion_servidor.get_historial_ventas(filtro)
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
            
            monto_str = f"${float(data.get('monto_total', 0.00)):,.2f}"

            row_data = [
                data.get("nombre_producto", "N/A"),
                data.get("categoria", "N/A"),
                data.get("cantidad", 0),
                data.get("fecha_venta", "N/A"),
                data.get("nombre_cliente", "N/A"),
                data.get("nombre_vendedor", "N/A"),
                monto_str
            ]
            
            for col, value in enumerate(row_data):
                customtkinter.CTkLabel(
                    self.ventas_tabla_frame,
                    text=str(value), 
                    anchor="w",
                    # 🚨 CLAVE: Texto negro para visibilidad sobre fondo claro
                    text_color="black",      
                    fg_color="transparent"  
                ).grid(row=row_index, column=col, padx=10, pady=PAD_Y, sticky="w")
                
            last_widget_row = row_index

        # Fila fantasma con peso 1 para forzar la expansión vertical
        fila_fantasma_index = last_widget_row + 1 if historial_ventas else 1
        self.ventas_tabla_frame.grid_rowconfigure(fila_fantasma_index, weight=1)
        customtkinter.CTkLabel(self.ventas_tabla_frame, text="", height=0, fg_color="transparent").grid(
            row=fila_fantasma_index,
            column=0,
            sticky="nsew"
        )

class MovimientoModal(customtkinter.CTkToplevel):
    def __init__(self, master, callback_reload, default_date=None, mode='create', movimiento_id=None, data=None):
        super().__init__(master)
        self.master_module = master # Guardamos una referencia al módulo principal
        self.title(f"{'Crear' if mode == 'create' else 'Editar'} Movimiento Logístico")
        self.geometry("650x560")
        self.transient(master) 
        self.grab_set() 
        self.callback_reload = callback_reload
        self.mode = mode
        self.movimiento_id = movimiento_id
        self.data = data if data else {}
        self.default_date = default_date

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = customtkinter.CTkFrame(self, fg_color=CELESTE_COLOR, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        self._create_widgets(main_frame)
    
    def _create_widgets(self, main_frame):
        
        # Título
        customtkinter.CTkLabel(main_frame, text=f"{'NUEVO' if self.mode == 'create' else 'EDITAR'} MOVIMIENTO LOGÍSTICO",
                               font=customtkinter.CTkFont(size=18, weight="bold"),
                               text_color="white").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # Frame contenedor para inputs
        form_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew") 
        form_frame.grid_columnconfigure(0, weight=1) 
        form_frame.grid_columnconfigure(1, weight=3) 
        form_frame.grid_rowconfigure(9, weight=1) # Fila de notas se expande

        row_num = 0
        PAD_Y_LABEL = 10 
        
        # --- Campos del formulario (Basado en tu imagen) ---

        # 1. Producto (OptionMenu)
        producto_nombres = [p['nombre'] for p in self.master_module.productos_list]
        default_producto = self.data.get('nombre_producto', producto_nombres[0] if producto_nombres else "N/A")
        if not producto_nombres:
            producto_nombres = ["N/A"]
            default_producto = "N/A"
            # Además, deshabilitamos el campo para evitar errores al guardar
            producto_state = "disabled"
        else:
            default_producto = self.data.get('nombre_producto', producto_nombres[0])
            producto_state = "normal"
            
        row_num = 0
        
        customtkinter.CTkLabel(form_frame, text="Producto:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        
        # 🚨 Inicializamos el OptionMenu
        self.option_producto = customtkinter.CTkOptionMenu(form_frame, 
                                                           values=producto_nombres, 
                                                           height=35,
                                                           state=producto_state) # Usamos el estado calculado
        
        self.option_producto.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        self.option_producto.set(default_producto)
        row_num += 1

        # 2. Tipo de Movimiento (OptionMenu)
        customtkinter.CTkLabel(form_frame, text="Tipo de Mov.:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        self.option_tipo = customtkinter.CTkOptionMenu(form_frame, values=TIPOS_MOVIMIENTO, height=35) 
        self.option_tipo.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        self.option_tipo.set(self.data.get('tipo', TIPOS_MOVIMIENTO[0]))
        row_num += 1
        
        # 3. Cantidad
        customtkinter.CTkLabel(form_frame, text="Cantidad:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        self.entry_cantidad = customtkinter.CTkEntry(form_frame, placeholder_text="Solo números", height=35)
        self.entry_cantidad.insert(0, str(self.data.get('cantidad', '')))
        self.entry_cantidad.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        row_num += 1

        # 4. Fecha de Movimiento
        customtkinter.CTkLabel(form_frame, text="Fecha Movimiento (YYYY-MM-DD):", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        self.entry_fecha = customtkinter.CTkEntry(form_frame, height=35)
        
        fecha_valor = self.data.get('fecha_movimiento')
        if not fecha_valor and self.default_date:
            fecha_valor = self.default_date
            
        self.entry_fecha.insert(0, fecha_valor if fecha_valor else datetime.now().strftime('%Y-%m-%d'))
        self.entry_fecha.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        row_num += 1
        
        # 5. Origen / Destino
        customtkinter.CTkLabel(form_frame, text="Origen / Destino:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        self.entry_origen_destino = customtkinter.CTkEntry(form_frame, placeholder_text="Ej: Almacén A -> Cliente Z", height=35)
        self.entry_origen_destino.insert(0, self.data.get('origen_destino', ''))
        self.entry_origen_destino.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        row_num += 1

        # 6. Transportista (FK) - Usaremos un Entry para simplificar
        # customtkinter.CTkLabel(form_frame, text="Transportista:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        # self.entry_transportista = customtkinter.CTkEntry(form_frame, height=35)
        # self.entry_transportista.insert(0, self.data.get('transportista', ''))
        # self.entry_transportista.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        # row_num += 1

        # 7. Estado (Pendiente / Completado / Cancelado)
        # customtkinter.CTkLabel(form_frame, text="Estado:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="w")
        # self.option_estado = customtkinter.CTkOptionMenu(form_frame, values=["Pendiente", "Completado", "Cancelado"], height=35)
        # self.option_estado.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="ew")
        # self.option_estado.set(self.data.get('estado', 'Pendiente'))
        # row_num += 1
        
        # 8. Notas (Text Box)
        # customtkinter.CTkLabel(form_frame, text="Notas:", anchor="w", text_color="white").grid(row=row_num, column=0, padx=10, pady=(PAD_Y_LABEL, 2), sticky="nw")
        # self.entry_notas = customtkinter.CTkTextbox(form_frame, height=100)
        # self.entry_notas.insert("0.0", self.data.get('notas', ''))
        # self.entry_notas.grid(row=row_num, column=1, padx=10, pady=(PAD_Y_LABEL, 2), sticky="nsew") 
        # row_num += 1

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
            text="Guardar Movimiento",
            command=self._save_movimiento,
            fg_color="#00bf63", 
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
        
    def _save_movimiento(self):
        # 1. Obtención de datos del formulario (Usando las etiquetas del cliente)
        producto_nombre = self.option_producto.get()
        tipo = self.option_tipo.get()
        cantidad = self.entry_cantidad.get()
        fecha = self.entry_fecha.get()
        origen_destino = self.entry_origen_destino.get()
        #transportista = self.entry_transportista.get() 
        #estado = self.option_estado.get() # Esta variable no se usa en BD, pero la mantenemos para el formulario
        #notas = self.entry_notas.get("0.0", "end-1c").strip()

        # Validaciones básicas
        if not all([producto_nombre, tipo, cantidad, fecha, origen_destino]):
            self.message_label.configure(text="Producto, Tipo, Cantidad, Fecha y Origen/Destino son obligatorios.")
            return

        try:
            int(cantidad)
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            self.message_label.configure(text="Cantidad debe ser entero. Fecha debe ser YYYY-MM-DD.")
            return
        
        producto_info = next((p for p in self.master_module.productos_list if p['nombre'] == producto_nombre), None)
        if not producto_info:
            self.message_label.configure(text=f"Error: Producto '{producto_nombre}' no encontrado.", text_color="red")
            return
            
        id_producto = producto_info['id_producto']

        # Datos a enviar (Usando los nombres de columna reales de la BD)
        movimiento_data = {
            "id_producto": id_producto,
            "tipo_movimiento": tipo, # Enviamos el tipo
            "cantidad": int(cantidad),
            "fecha_movimiento": fecha,
            "origen_destino": origen_destino
        }
        
        try:
            # 3. Lógica de Envío al Servidor (POST o PUT)
            if self.mode == 'create':
                success, message = conexion_servidor.create_movimiento(movimiento_data) 
            else:
                success, message = conexion_servidor.update_movimiento(self.movimiento_id, movimiento_data)
            
            if success:
                messagebox.showinfo("Éxito", message)
                self.callback_reload() 
                self.destroy()
            else:
                self.message_label.configure(text=f"Error: {message}", text_color="red")
        except Exception as e:
            self.message_label.configure(text=f"Error de conexión: {e}", text_color="red")