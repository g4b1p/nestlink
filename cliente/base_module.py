import customtkinter 
from tkinter import messagebox 
from PIL import Image 
import os
import sys

# Definición del color celeste/azul vibrante 
CELESTE_COLOR = "#3498DB" # Color de acento para botones, etc.
BORDO_COLOR = "#b26555"

# NUEVOS COLORES DE FONDO INSPIRADOS EN EL DISEÑO
MAIN_BG_COLOR = "#ccdae7" # 🚨 CAMBIO AQUÍ: Azul suave/gris para el fondo principal de la aplicación
SIDEBAR_COLOR = "#3A669A" # Azul oscuro/opaco para la barra lateral
CONTENT_BG_COLOR = "white" # Color blanco para el área de contenido (tablas)

# DEFINIMOS EL LOGO DE NESTLINK
# La ruta correcta es 'images/' que está al mismo nivel que base_module.py
_base_path = os.path.join(os.path.dirname(__file__), 'images') 
try:
    NESTLINK_LOGO = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(_base_path, 'logo-nestlink.png')),
        dark_image=Image.open(os.path.join(_base_path, 'logo-nestlink.png')),
        size=(80, 80)
    )
    NESTLINK_LOGO_FULL = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(_base_path, 'logo-nestlink.png')),
        dark_image=Image.open(os.path.join(_base_path, 'logo-nestlink.png')),
        size=(180, 80)
    )
    
except FileNotFoundError:
    print("Advertencia: No se encontró 'logo-nestlink.png'. Usando texto.")
    NESTLINK_LOGO = None
    NESTLINK_LOGO_FULL = None  

class BaseAppWindow(customtkinter.CTkToplevel): 
    """Ventana base para todos los módulos de la aplicación (Dashboard).""" 
    
    MODULE_HEADER_ICON = None
    
    def __init__(self, master, title, user_info): 
        
        super().__init__(master) 
        self.master = master 
        self.user_info = user_info 
        
        self.title(f"Nestlink ERP - Módulo de {title}") 
        self.configure(fg_color=MAIN_BG_COLOR)
        
        screen_width = self.winfo_screenwidth() 
        screen_height = self.winfo_screenheight() 
        window_width = int(screen_width * 0.8) 
        window_height = int(screen_height * 0.8) 
        center_x = int((screen_width - window_width) / 2) 
        center_y = int((screen_height - window_height) / 2) 

        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}") 
        self.minsize(800, 600) 
        
        self.grab_set() 
        self.master.withdraw() 
        self.protocol("WM_DELETE_WINDOW", self.logout) 
        
        # Configuración de layout principal (2 columnas)
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Contenido principal
        
        # ------------------- 1. Barra Lateral (Sidebar) ------------------- 
        self.sidebar_frame = customtkinter.CTkFrame(self, width=220, corner_radius=0, fg_color=SIDEBAR_COLOR) 
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew") 
        self.sidebar_frame.grid_rowconfigure(0, weight=0) 
        self.sidebar_frame.grid_columnconfigure(0, weight=1) 
        self.sidebar_frame.grid_rowconfigure(98, weight=1) 
        self.sidebar_frame.grid_rowconfigure(99, weight=0) 
        
        # Título/Logo
        if NESTLINK_LOGO:
            customtkinter.CTkLabel(self.sidebar_frame, text="", image=NESTLINK_LOGO).grid(row=0, column=0, padx=20, pady=(20, 10))
        else:
            customtkinter.CTkLabel(self.sidebar_frame, text="Nestlink", font=customtkinter.CTkFont(size=20, weight="bold"), text_color="white").grid(row=0, column=0, padx=20, pady=(20, 10))
            
        self.sidebar_button_frames = [] 
        
        # ------------------- 2. Contenido Principal ------------------- 
        self.main_content_frame = customtkinter.CTkFrame(self, fg_color=MAIN_BG_COLOR)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        
        # El contenido principal tiene 2 filas (Header y Área de Trabajo)
        self.main_content_frame.grid_columnconfigure(0, weight=1) 
        self.main_content_frame.grid_rowconfigure(0, weight=0) # Header Fijo (no se expande)
        self.main_content_frame.grid_rowconfigure(1, weight=1) # Área de Trabajo (se expande)
        
        # Header Bar Fijo (Fila 0)
        self._setup_header_bar(title, self.MODULE_HEADER_ICON)

        # Área de Trabajo Blanca (Fila 1)
        self.white_content_area = customtkinter.CTkFrame(self.main_content_frame, fg_color=MAIN_BG_COLOR, corner_radius=0)
        self.white_content_area.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew") 
        self.white_content_area.grid_columnconfigure(0, weight=1) 
        self.white_content_area.grid_rowconfigure(0, weight=1) 
        
        # self.main_content: Marco transparente dentro del área blanca para las vistas
        self.main_content = customtkinter.CTkFrame(self.white_content_area, fg_color="transparent") 
        self.main_content.grid(row=0, column=0, sticky="nsew") 
        self.main_content.grid_columnconfigure(0, weight=1) 
        
        # Contenido inicial de ejemplo 
        welcome_text = f"Hola, {user_info.get('username', 'Usuario')}. Estás en el módulo de {title}." 
        self.initial_label = customtkinter.CTkLabel(self.main_content, text=welcome_text, font=customtkinter.CTkFont(size=20)) 
        self.initial_label.pack(padx=50, pady=50)


    def _setup_header_bar(self, title, module_icon):
        """
        Crea la barra superior con el título del módulo, su ícono, la información del usuario 
        y el botón de cerrar sesión, aplicando los estilos solicitados.
        """
        header_frame = customtkinter.CTkFrame(self.main_content_frame, fg_color=CONTENT_BG_COLOR, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="new", padx=0, pady=0) 
        
        INTERNAL_PADDING_X = 30
        INTERNAL_PADDING_Y = 15
        
        header_frame.grid_columnconfigure(0, weight=0) # Ícono del Módulo
        header_frame.grid_columnconfigure(1, weight=1) # Título del Módulo (Expande)
        header_frame.grid_columnconfigure(2, weight=0) # Usuario
        header_frame.grid_columnconfigure(3, weight=0) # Botón Cerrar Sesión
        
        # 1. Ícono del Módulo (Izquierda)
        if module_icon:
            icon_container = customtkinter.CTkFrame(header_frame, fg_color="transparent", width=40, height=40)
            icon_container.grid(row=0, column=0, sticky="w", padx=(INTERNAL_PADDING_X, 0), pady=INTERNAL_PADDING_Y)
            icon_container.grid_propagate(False)
            
            icon_label = customtkinter.CTkLabel(icon_container, text="", image=module_icon)
            icon_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            icon_container.grid_columnconfigure(0, weight=1)
            icon_container.grid_rowconfigure(0, weight=1)
        
        # 2. Título del Módulo (Al lado del ícono)
        # ✅ CAMBIO 1: Color (#5b94c6) y Tamaño (size=22) del Título Principal
        customtkinter.CTkLabel(
            header_frame, 
            text=f"Módulo de {title}", 
            font=customtkinter.CTkFont(size=22, weight="bold"),
            text_color="#5b94c6" 
        ).grid(row=0, column=1, sticky="w", padx=10, pady=INTERNAL_PADDING_Y) 
        
        # 3. Nombre de Usuario (Centro-Derecha)
        user_name = self.user_info.get('username', 'Usuario')
        # ✅ CAMBIO 2: Color (#5b94c6) del Nombre de Usuario
        customtkinter.CTkLabel(
            header_frame, 
            text=user_name, 
            text_color="#5b94c6"
        ).grid(row=0, column=2, padx=10, pady=INTERNAL_PADDING_Y, sticky="e") 
        
        # 4. Botón Cerrar Sesión (Derecha)
        customtkinter.CTkButton(
            header_frame,
            text="Cerrar Sesión",
            command=self.logout,
            fg_color=BORDO_COLOR,
            hover_color="#C0392B",
            text_color="white",
            width=100,
            height=35
        ).grid(row=0, column=3, padx=(0, INTERNAL_PADDING_X), pady=INTERNAL_PADDING_Y, sticky="e")
        
        
    def logout(self): 
        """
        Cierra la ventana del módulo y vuelve a mostrar la ventana principal (Login).
        """ 
        self.master.deiconify() 
        self.destroy() 


    def _set_sidebar_buttons(self, config): 
        """ 
        Crea los botones de navegación en la barra lateral basados en la configuración. 
        """ 
        for btn_frame in self.sidebar_button_frames: 
            btn_frame.destroy() 
        self.sidebar_button_frames.clear() 

        for i, (text, command, icon) in enumerate(config): 
            
            btn_container_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color=SIDEBAR_COLOR, corner_radius=10)
            btn_container_frame.grid(row=i + 1, column=0, padx=15, pady=5, sticky="ew")
            btn_container_frame.grid_columnconfigure(0, weight=1)

            button = customtkinter.CTkButton( 
                btn_container_frame, 
                text=text, 
                command=command, 
                compound="left", 
                image=icon if icon else None, 
                anchor="w",
                fg_color="transparent",
                text_color="white",   
                hover_color="#2A5380"  
            ) 
            button.grid(row=0, column=0, sticky="ew", padx=5, pady=5) 
            self.sidebar_button_frames.append(btn_container_frame) 


    def _clear_main_content(self): 
        """ 
        Destruye el contenido actual dentro de self.main_content 
        y resetea la configuración de la grilla para una nueva vista. 
        """ 
        for widget in self.main_content.winfo_children(): 
            widget.destroy() 
        
        self.main_content.grid_columnconfigure(0, weight=1) 
        self.main_content.grid_rowconfigure(0, weight=0) 
        self.main_content.grid_rowconfigure(1, weight=0)