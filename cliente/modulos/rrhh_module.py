import customtkinter 
from tkinter import filedialog, messagebox 
import os 
import sys 
from datetime import datetime 
from PIL import Image 

# Importamos la librería de conexión al servidor (ASUME QUE EXISTE) 
import conexion_servidor # 🚨 Asegúrate de que esta librería exista

# Importación limpia de la clase base y la variable de color 
# 🚨 Asegúrate de que 'MAIN_BG_COLOR' esté definido en base_module.py como #ccdae7
from base_module import BaseAppWindow, CELESTE_COLOR, SIDEBAR_COLOR, MAIN_BG_COLOR 

# ================================================================= 
# CARGAR ÍCONOS DE MÓDULO (Para el Header y la Sidebar) 
# ================================================================= 

_base_path = os.path.join(os.path.dirname(__file__), '..', 'images')

# 🚨 ÍCONO PARA EL HEADER (rrhh-logo.png)
ICON_MODULO_RRHH = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'rrhh-logo.png')), 
    dark_image=Image.open(os.path.join(_base_path, 'rrhh-logo.png')), 
    size=(30, 30)
)

# ÍCONOS PARA LA SIDEBAR
ICON_POSTULANTE = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'gestión-postulantes.png')), 
    dark_image=Image.open(os.path.join(_base_path, 'gestión-postulantes.png')), 
    size=(30, 30)
) 
ICON_CAPACITACION = customtkinter.CTkImage(
    light_image=Image.open(os.path.join(_base_path, 'registro-capacitaciones.png')), 
    dark_image=Image.open(os.path.join(_base_path, 'registro-capacitaciones.png')), 
    size=(30, 30)
) 

# ================================================================= 
# FUNCIÓN DE UTILIDAD: Formateo de Fechas 
# ================================================================= 

def _formatear_fecha(fecha_str): 
    """ 
    Intenta limpiar y reformatear una cadena de fecha. 
    """ 
    if not fecha_str: 
        return "N/A" 
        
    try: 
        # Manejo del formato de error o placeholder
        if '%%Y-%%m-%%d' in fecha_str:
            return "Formato Pendiente" 
            
        # Asume que el formato correcto de la BD es 'YYYY-MM-DD' (con o sin tiempo)
        fecha_obj = datetime.strptime(fecha_str.split()[0], '%Y-%m-%d') 
        return fecha_obj.strftime('%Y-%m-%d') 
        
    except ValueError: 
        return str(fecha_str) 

# ================================================================= 
# CLASE ESPECÍFICA PARA RECURSOS HUMANOS 
# ================================================================= 

class RRHHModule(BaseAppWindow): 
    """Módulo para Recursos Humanos, gestionando Candidatos y Capacitaciones.""" 
    
    # 🚨 ASIGNACIÓN DEL ÍCONO AL HEADER
    MODULE_HEADER_ICON = ICON_MODULO_RRHH
    
    # Asignación de los íconos de la sidebar (definidos arriba)
    ICON_POSTULANTE = ICON_POSTULANTE
    ICON_CAPACITACION = ICON_CAPACITACION


    def __init__(self, master, user_info): 
        
        super().__init__(master, "Recursos Humanos", user_info) 
        
        buttons_config = [ 
            ("Gestión de Candidatos", self._show_postulantes_view, self.ICON_POSTULANTE), 
            ("Registro de Capacitaciones", self._show_capacitaciones_view, self.ICON_CAPACITACION), 
        ] 
        
        self._set_sidebar_buttons(buttons_config) 
        
        self._show_postulantes_view() 

    # ----------------------------------------------------------------- 
    # VISTA 1: GESTIÓN DE POSTULANTES (CANDIDATOS) 
    # ----------------------------------------------------------------- 

    def _show_postulantes_view(self): 
        """Muestra la interfaz para la gestión y listado de postulantes/candidatos.""" 
        self._clear_main_content() 
        
        # 🚨 CONFIGURACIÓN CLAVE: La tabla (fila 1) se expande vertical y horizontalmente.
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # --- 1. Header de la Vista (Título, Botón Agregar y Filtro) --- 
        view_header_frame = customtkinter.CTkFrame(self.main_content, fg_color="transparent")
        view_header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        view_header_frame.grid_columnconfigure(0, weight=1)
        view_header_frame.grid_columnconfigure(1, weight=0)
        view_header_frame.grid_columnconfigure(2, weight=0)
        
        customtkinter.CTkLabel(view_header_frame, text="Gestión de Candidatos", font=customtkinter.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w") 
        
        # Filtro (CTkOptionMenu) 
        estados = ["Todos los estados", "Recibido", "En revisión", "Entrevista agendada", "Contratado", "Descartado", "En proceso de selección"] 
        self.postulantes_filtro = customtkinter.CTkOptionMenu( 
            view_header_frame, 
            values=estados, 
            command=self._filtrar_postulantes_tabla, 
            width=200 
        ) 
        self.postulantes_filtro.grid(row=0, column=1, padx=(0, 15), sticky="e") 

        # Botón Agregar Candidatos
        customtkinter.CTkButton(
            view_header_frame,
            text="+ Agregar Postulante", 
            command=self._open_agregar_postulante_modal,
            fg_color="#00bf63", 
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

        columnas = ["Nombre", "Email", "Estado", "Fecha Post.", "Acciones"]
        NUM_COLUMNAS_DATOS = len(columnas)
        
        # 🚨 PASO 2: Frame para la CABECERA FIJA (row=0 del table_border_container)
        self.header_fixed_frame = customtkinter.CTkFrame(
            self.table_border_container,
            fg_color="#5b94c6", # Color Azul de la Cabecera
            corner_radius=0
        )
        # Ojo con el padding para evitar que se coma el borde.
        self.header_fixed_frame.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0)) 
        
        # CLAVE A: COMPENSACIÓN SCROLLBAR (Columna extra con minsize=17, sin peso)
        # Esto reserva el espacio que usará el scrollbar en el frame de abajo.
        self.header_fixed_frame.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17) 
        
        # BUCLE DE CONFIGURACIÓN Y ETIQUETAS DEL ENCABEZADO
        for i, col_name in enumerate(columnas):
            # CLAVE B: Pesos de columna idénticos a los del cuerpo
            self.header_fixed_frame.grid_columnconfigure(i, weight=(1 if i < 4 else 0)) 
            customtkinter.CTkLabel(
                self.header_fixed_frame, 
                text=col_name, 
                font=customtkinter.CTkFont(weight="bold", size=13),
                text_color="white" 
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")
        
        # 🚨 PASO 3: CTkScrollableFrame (la tabla de datos) (row=1 del table_border_container)
        self.postulantes_tabla_frame = customtkinter.CTkScrollableFrame(
            self.table_border_container, 
            fg_color="transparent" 
        )
        self.postulantes_tabla_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2)) 
        
        # CLAVE C: Configuramos las columnas del cuerpo para que coincidan con la cabecera.
        # Esto es crucial para la alineación horizontal.
        for i in range(len(columnas)):
            self.postulantes_tabla_frame.grid_columnconfigure(i, weight=(1 if i < 4 else 0)) 

        # Finalmente, cargamos los datos
        self._load_postulantes_data(estado_filtro=self.postulantes_filtro.get())


    def _load_postulantes_data(self, estado_filtro): 
        """Carga datos del servidor (BD) y construye las filas de datos.""" 
        # Solo destruye los WIDGETS DE DATOS dentro del ScrollableFrame
        for widget in self.postulantes_tabla_frame.winfo_children(): 
            widget.destroy() 

        # --- Obtención de Datos DEL SERVIDOR --- 
        try: 
            if estado_filtro == "Todos los estados":
                datos_postulantes = conexion_servidor.get_candidatos(None) 
            else:
                datos_postulantes = conexion_servidor.get_candidatos(estado_filtro)
                
        except Exception as e: 
            messagebox.showerror("Error de Carga", f"No se pudieron cargar los postulantes: {e}") 
            datos_postulantes = []
        
        # --- Filas de Datos --- 
        if not datos_postulantes:
            customtkinter.CTkLabel(self.postulantes_tabla_frame, text="No se encontraron postulantes con este filtro.", text_color="gray").grid(row=0, column=0, columnspan=5, padx=10, pady=20)
            return

        PAD_UNIFORME_Y = 5 # Padding vertical para centrado visual
        
        # 🚨 CORRECCIÓN DEL ATRIBUTO ERROR: Accede a self.postulantes_filtro
        try:
             estados_menu = list(self.postulantes_filtro.cget("values"))[1:]
        except:
             estados_menu = ["Recibido", "En revisión", "Entrevista agendada", "Contratado", "Descartado", "En proceso de selección"]

        for row, data in enumerate(datos_postulantes): 
            row_index = row # La primera fila de datos es la fila 0
            candidato_id = data.get("id", row + 1) 
            
            items = [data.get("nombre", "N/A"), data.get("email", "N/A"), _formatear_fecha(data.get("fecha_post", "N/A"))]
            
            # 1. Nombre (Col 0)
            customtkinter.CTkLabel(self.postulantes_tabla_frame, text=items[0]).grid(row=row_index, column=0, padx=10, pady=PAD_UNIFORME_Y, sticky="w")
            
            # 2. Email (Col 1)
            customtkinter.CTkLabel(self.postulantes_tabla_frame, text=items[1]).grid(row=row_index, column=1, padx=10, pady=PAD_UNIFORME_Y, sticky="w")
            
            # 3. Columna Estado (CTkOptionMenu) (Columna 2) 
            estado_menu = customtkinter.CTkOptionMenu( 
                self.postulantes_tabla_frame, 
                values=estados_menu, 
                command=lambda new_state, id=candidato_id: self._actualizar_estado_postulante(id, new_state), 
                width=180 
            ) 
            estado_menu.set(data.get("estado", "Recibido")) 
            estado_menu.grid(row=row_index, column=2, padx=10, pady=PAD_UNIFORME_Y, sticky="w") 
            
            # 4. Fecha Post. (Col 3) 
            customtkinter.CTkLabel(self.postulantes_tabla_frame, text=items[2]).grid(row=row_index, column=3, padx=10, pady=PAD_UNIFORME_Y, sticky="w") 
            
            # 5. Columna Acciones (Botón Ver CV) (Columna 4) 
            ver_cv_btn = customtkinter.CTkButton( 
                self.postulantes_tabla_frame, 
                text="Ver CV", 
                command=lambda id=candidato_id: self._ver_cv_postulante(id), 
                width=80, 
                fg_color="gray", 
                hover_color="gray50" 
            ) 
            ver_cv_btn.grid(row=row_index, column=4, padx=10, pady=PAD_UNIFORME_Y, sticky="w")


    def _filtrar_postulantes_tabla(self, estado_seleccionado): 
        """Función que se llama al cambiar el filtro.""" 
        self._load_postulantes_data(estado_seleccionado) 

    def _actualizar_estado_postulante(self, candidato_id, nuevo_estado): 
        """Llama a la función de conexión para actualizar el estado del candidato.""" 
        if nuevo_estado in ["Actualizar"]: return 
        
        try: 
            success = conexion_servidor.actualizar_estado_candidato_db(candidato_id, nuevo_estado) 
            if success: 
                messagebox.showinfo("Actualización Exitosa", f"Estado de Candidato ID:{candidato_id} actualizado a: {nuevo_estado}") 
            else:
                messagebox.showerror("Error", "No se pudo encontrar o actualizar el candidato en el servidor.")
        except Exception as e: 
            messagebox.showerror("Error", f"Error de comunicación al actualizar: {e}") 

        self._load_postulantes_data(self.postulantes_filtro.get())

    def _ver_cv_postulante(self, candidato_id): 
        """Función que simula la descarga y visualización del CV.""" 
        messagebox.showinfo("Ver CV", f"Llamada GET /candidatos/{candidato_id}/cv. Abriendo PDF simulado...") 

    def _open_agregar_postulante_modal(self): 
        """Abre la ventana modal (Toplevel) para añadir un nuevo postulante.""" 
        modal = AgregarPostulanteModal(self) 
        modal.grab_set() 


    # ----------------------------------------------------------------- 
    # VISTA 2: REGISTRO DE CAPACITACIONES 
    # ----------------------------------------------------------------- 
    
    
    def _show_capacitaciones_view(self): 
        """Muestra la interfaz para el listado de empleados y su historial, con cabecera fija, borde y diseño alineado a Candidatos.""" 
        self._clear_main_content() 
        
        # 🚨 CONFIGURACIÓN CLAVE: La tabla (fila 1) se expande vertical y horizontalmente.
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # --- 1. Header de la Vista (Título y Buscador) --- 
        view_header_frame = customtkinter.CTkFrame(self.main_content, fg_color="transparent") 
        view_header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20) 
        view_header_frame.grid_columnconfigure(0, weight=1) 
        view_header_frame.grid_columnconfigure(1, weight=0) 
        
        customtkinter.CTkLabel(view_header_frame, text="Registro de Capacitaciones", font=customtkinter.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w") 
        
        # Buscador (CTkEntry) 
        self.empleados_buscador = customtkinter.CTkEntry( 
            view_header_frame, 
            placeholder_text="Buscar empleado por nombre...", 
            width=250, 
        ) 
        self.empleados_buscador.grid(row=0, column=1, padx=(0, 0), sticky="e") 
        self.empleados_buscador.bind("<KeyRelease>", self._filtrar_empleados_tabla) 

        # -----------------------------------------------------------------------
        # 2. Área de la Tabla (Contenedor con Borde, Cabecera FIJA y ScrollableFrame) 
        # -----------------------------------------------------------------------
        
        # PASO 1: Contenedor que maneja el Borde (border_width=2 y fg_color=MAIN_BG_COLOR)
        self.table_border_container_capacitaciones = customtkinter.CTkFrame(
            self.main_content, 
            corner_radius=5,
            fg_color=MAIN_BG_COLOR, 
            border_color="#5b94c6", 
            border_width=2 
        )
        self.table_border_container_capacitaciones.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20)) 
        
        self.table_border_container_capacitaciones.grid_columnconfigure(0, weight=1)
        self.table_border_container_capacitaciones.grid_rowconfigure(0, weight=0) # Cabecera fija
        self.table_border_container_capacitaciones.grid_rowconfigure(1, weight=1) # Cuerpo scrollable (CLAVE)

        columnas = ["Nombre", "Sector", "Acciones"]
        NUM_COLUMNAS_DATOS = len(columnas)
        
        # 🚨 PASO 2: Frame para la CABECERA FIJA
        self.header_fixed_frame_capacitaciones = customtkinter.CTkFrame(
            self.table_border_container_capacitaciones,
            fg_color="#5b94c6", 
            corner_radius=0
        )
        # Márgenes de la Cabecera: padx=1, pady=(1, 0)
        self.header_fixed_frame_capacitaciones.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0)) 
        
        # CLAVE A: COMPENSACIÓN SCROLLBAR (Columna extra con minsize=17)
        self.header_fixed_frame_capacitaciones.grid_columnconfigure(NUM_COLUMNAS_DATOS, weight=0, minsize=17) 
        
        # BUCLE DE CONFIGURACIÓN Y ETIQUETAS DEL ENCABEZADO
        for i, col_name in enumerate(columnas):
            # Pesos de columna: Las primeras 2 se expanden (weight=1), la 3ra (Acciones) no (weight=0).
            self.header_fixed_frame_capacitaciones.grid_columnconfigure(i, weight=(1 if i < 2 else 0)) 
            customtkinter.CTkLabel(
                self.header_fixed_frame_capacitaciones, 
                text=col_name, 
                font=customtkinter.CTkFont(weight="bold", size=13),
                text_color="white" 
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")
        
        # 🚨 PASO 3: CTkScrollableFrame (la tabla de datos) 
        self.empleados_tabla_frame = customtkinter.CTkScrollableFrame(
            self.table_border_container_capacitaciones, 
            fg_color="transparent" 
        )
        # ✅ CLAVE: Márgenes del cuerpo (copiado de Candidatos): padx=2, pady=(0, 2)
        self.empleados_tabla_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2)) 
        
        # Configuramos las columnas del cuerpo para que coincidan con la cabecera.
        for i in range(len(columnas)):
            self.empleados_tabla_frame.grid_columnconfigure(i, weight=(1 if i < 2 else 0)) 

        self._load_empleados_data(nombre_filtro="")
    

    def _filtrar_empleados_tabla(self, event): 
        """Función que se llama al escribir en el buscador.""" 
        nombre_filtro = self.empleados_buscador.get() 
        self._load_empleados_data(nombre_filtro) 


    def _load_empleados_data(self, nombre_filtro): 
        """Carga empleados reales del servidor y los inserta en la tabla, SIN dibujar la cabecera.""" 
        for widget in self.empleados_tabla_frame.winfo_children(): 
            widget.destroy() 

        # --- Obtención de Datos DEL SERVIDOR --- 
        try: 
            empleados = conexion_servidor.get_empleados(nombre_filtro) 
            
        except Exception as e: 
            messagebox.showerror("Error de Carga", f"No se pudieron cargar los empleados: {e}") 
            empleados = []

        # --- Filas de Datos (Cuerpo de la Tabla) --- 
        PAD_UNIFORME_Y = 5
        
        if not empleados:
            # Fila 0 para el mensaje
            customtkinter.CTkLabel(self.empleados_tabla_frame, text="No se encontraron empleados activos con este filtro.", text_color="gray").grid(row=0, column=0, columnspan=3, padx=10, pady=20)
            last_widget_row = 0
            
        else:
            for row, data in enumerate(empleados): 
                row_index = row # La primera fila de datos es la fila 0
                empleado_id = data.get("id", row + 1) 
                
                # Datos (Nombre, Sector) 
                items = [data.get("nombre", ""), data.get("sector", "")] 
                
                # 1. Nombre (Col 0)
                customtkinter.CTkLabel(self.empleados_tabla_frame, text=items[0]).grid(row=row_index, column=0, padx=10, pady=PAD_UNIFORME_Y, sticky="w") 
                
                # 2. Sector (Col 1)
                customtkinter.CTkLabel(self.empleados_tabla_frame, text=items[1]).grid(row=row_index, column=1, padx=10, pady=PAD_UNIFORME_Y, sticky="w") 
                
                # 3. Columna Acciones (Ver Historial) (Col 2)
                ver_historial_btn = customtkinter.CTkButton( 
                    self.empleados_tabla_frame, 
                    text="Ver Historial", 
                    command=lambda id=empleado_id, name=data.get("nombre", ""): self._show_historial_modal(id, name), 
                    width=100 
                ) 
                ver_historial_btn.grid(row=row_index, column=2, padx=10, pady=PAD_UNIFORME_Y, sticky="w") 
            
            last_widget_row = len(empleados) - 1

        # 🚀 SOLUCIÓN CLAVE: Fila fantasma con peso 1 para forzar la expansión vertical.
        fila_fantasma_index = last_widget_row + 1 if empleados else 1
        
        self.empleados_tabla_frame.grid_rowconfigure(fila_fantasma_index, weight=1) 
        
        # Agregamos un widget invisible para asegurar la aplicación del weight=1.
        customtkinter.CTkLabel(self.empleados_tabla_frame, text="", height=0, fg_color="transparent").grid(
            row=fila_fantasma_index, 
            column=0, 
            sticky="nsew"
        )


    def _show_historial_modal(self, empleado_id, nombre_empleado): 
        """Muestra el historial de capacitaciones de un empleado en un pop-up.""" 
        modal = HistorialCapacitacionesModal(self, empleado_id, nombre_empleado) 
        modal.grab_set() 


# ================================================================= 
# MODAL: Agregar Postulante 
# ================================================================= 

class AgregarPostulanteModal(customtkinter.CTkToplevel): 
    
    def __init__(self, master): 
        super().__init__(master) 
        self.master = master 
        self.title("Agregar Nuevo Candidato") 
        self.geometry("450x350") 
        self.resizable(False, False) 
        self.cv_filepath = None 

        self.grid_columnconfigure(0, weight=1) 
        
        customtkinter.CTkLabel(self, text="Datos del Candidatos", font=customtkinter.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=20) 
        
        self.nombre_entry = customtkinter.CTkEntry(self, placeholder_text="Nombre Completo", width=350) 
        self.nombre_entry.grid(row=1, column=0, pady=10) 
        
        self.email_entry = customtkinter.CTkEntry(self, placeholder_text="Email", width=350) 
        self.email_entry.grid(row=2, column=0, pady=10) 
        
        cv_frame = customtkinter.CTkFrame(self, fg_color="transparent") 
        cv_frame.grid(row=3, column=0, pady=10) 
        cv_frame.grid_columnconfigure(0, weight=1) 
        
        self.cv_path_label = customtkinter.CTkLabel(cv_frame, text="Ningún archivo seleccionado", text_color="gray") 
        self.cv_path_label.grid(row=0, column=0, sticky="w", padx=(0, 10)) 

        customtkinter.CTkButton(cv_frame, text="Subir CV...", command=self._seleccionar_cv, width=100).grid(row=0, column=1) 

        # 🎨 Botón Guardar Postulante: Mantiene el color CELESTE
        customtkinter.CTkButton(self, text="Guardar Candidato", command=self._guardar_postulante, fg_color=CELESTE_COLOR).grid(row=4, column=0, pady=20) 


    def _seleccionar_cv(self): 
        """Abre el diálogo para seleccionar el archivo CV.""" 
        filepath = filedialog.askopenfilename( 
            defaultextension=".pdf", 
            filetypes=[("Archivos PDF", "*.pdf"), ("Archivos DOCX", "*.docx")] 
        ) 
        if filepath: 
            self.cv_path_label.configure(text=os.path.basename(filepath), text_color="green") 
            self.cv_filepath = filepath 
        else: 
            self.cv_path_label.configure(text="Ningún archivo seleccionado", text_color="gray") 
            self.cv_filepath = None 

    def _guardar_postulante(self): 
        """Maneja el envío de datos al servidor (POST /candidatos).""" 
        nombre = self.nombre_entry.get() 
        email = self.email_entry.get() 
        
        if not nombre or not email: 
            messagebox.showerror("Error", "El nombre y el email son obligatorios.") 
            return 

        messagebox.showinfo("Guardar", f"Enviando POST /candidatos con Nombre: {nombre}, Email: {email} y CV adjunto (simulado).") 
        
        # Recargar tabla del módulo principal para ver el nuevo registro 
        self.master._load_postulantes_data(self.master.postulantes_filtro.get()) 
        self.destroy() 


# ================================================================= 
# MODAL: Historial de Capacitaciones 
# ================================================================= 

class HistorialCapacitacionesModal(customtkinter.CTkToplevel): 
    
    def __init__(self, master, empleado_id, nombre_empleado): 
        super().__init__(master) 
        self.empleado_id = empleado_id 
        self.nombre_empleado = nombre_empleado 
        self.title(f"Historial de {nombre_empleado}") 
        self.geometry("600x400") 
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1) 

        customtkinter.CTkLabel(self, text=f"Historial de Formación: {nombre_empleado}", font=customtkinter.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=10) 
        
        self.historial_frame = customtkinter.CTkScrollableFrame(self, corner_radius=5, label_text="Capacitaciones Completadas") 
        self.historial_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20) 
        
        self._load_historial() 

    def _load_historial(self): 
        """Carga el historial de capacitaciones del empleado desde el servidor.""" 
        
        for widget in self.historial_frame.winfo_children(): 
            widget.destroy() 

        # --- Obtención de Datos DEL SERVIDOR --- 
        try: 
            historial = conexion_servidor.get_capacitaciones_empleado(self.empleado_id) 
            
        except Exception as e: 
            messagebox.showerror("Error de Carga", f"No se pudo cargar el historial: {e}") 
            historial = [] 
            
        # Cabecera 
        customtkinter.CTkLabel(self.historial_frame, text="Nombre de Capacitación", font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w") 
        customtkinter.CTkLabel(self.historial_frame, text="Fecha de Finalización", font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w") 
        
        self.historial_frame.grid_columnconfigure(0, weight=1) 
        
        # Filas 
        if not historial: 
            customtkinter.CTkLabel(self.historial_frame, text="No hay historial registrado.", text_color="gray").grid(row=1, column=0, columnspan=2, padx=10, pady=20)
            return
            
        for row, data in enumerate(historial): 
            nombre_curso = data.get("curso", "") 
            
            fecha_cruda = data.get("fecha", "") 
            fecha_limpia = _formatear_fecha(fecha_cruda) 
            
            customtkinter.CTkLabel(self.historial_frame, text=nombre_curso).grid(row=row + 1, column=0, padx=10, pady=5, sticky="w") 
            customtkinter.CTkLabel(self.historial_frame, text=fecha_limpia).grid(row=row + 1, column=1, padx=10, pady=5, sticky="w")