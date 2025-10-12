import customtkinter 
from tkinter import messagebox 

# Definición del color celeste/azul vibrante 
CELESTE_COLOR = "#3498DB"  

class BaseAppWindow(customtkinter.CTkToplevel): 
    """Ventana base para todos los módulos de la aplicación (Dashboard).""" 
    
    def __init__(self, master, title, user_info): 
        
        super().__init__(master) 
        self.master = master 
        self.user_info = user_info 
        
        self.title(f"Nestlink ERP - Módulo de {title}") 
        
        # 🚨 CORRECCIÓN CLAVE: Definir las variables de geometría antes de usarlas
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
        
        # Configuración de layout principal (Ahora con 2 columnas: Sidebar y Contenido) 
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        
        # ------------------- 1. Barra Lateral (Sidebar) ------------------- 
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0) 
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew") 
        self.sidebar_frame.grid_rowconfigure(0, weight=0) # Logo/Titulo
        self.sidebar_frame.grid_columnconfigure(0, weight=1) 
        self.sidebar_frame.grid_rowconfigure(98, weight=1) # Espacio flexible
        self.sidebar_frame.grid_rowconfigure(99, weight=0) # Botón Cerrar Sesión
        
        # Título del Menú 
        customtkinter.CTkLabel(self.sidebar_frame, text=f"Menú de {title}", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10)) 
        
        self.sidebar_button_frames = [] # Lista para guardar los botones modulares 
        
        self.logout_button = customtkinter.CTkButton(self.sidebar_frame,  
                                                     text="Cerrar Sesión",  
                                                     command=self.logout,  
                                                     fg_color="#E74C3C") 
        self.logout_button.grid(row=99, column=0, padx=20, pady=(10, 20), sticky="s") 
        
        
        # ------------------- 2. Contenido Principal ------------------- 
        self.main_content_frame = customtkinter.CTkFrame(self, fg_color="transparent") 
        self.main_content_frame.grid(row=0, column=1, sticky="nsew") 
        self.main_content_frame.grid_columnconfigure(0, weight=1) 
        self.main_content_frame.grid_rowconfigure(0, weight=1) 
        
        # 🚨 CAMBIO CLAVE: self.main_content es ahora un CTkFrame simple (NO scrollable)
        # Esto permite que su contenido interno (las tablas) se estiren correctamente.
        self.main_content = customtkinter.CTkFrame(self.main_content_frame, fg_color="transparent") 
        self.main_content.grid(row=0, column=0, padx=20, pady=20, sticky="nsew") 
        self.main_content.grid_columnconfigure(0, weight=1) 
        
        # Contenido inicial de ejemplo 
        welcome_text = f"Hola, {user_info.get('username', 'Usuario')}. Estás en el módulo de {title}." 
        self.initial_label = customtkinter.CTkLabel(self.main_content, text=welcome_text, font=customtkinter.CTkFont(size=20)) 
        self.initial_label.pack(padx=50, pady=50) 


    def logout(self): 
        """Cierra la ventana del módulo y vuelve a mostrar la ventana principal (Login).""" 
        self.master.deiconify()  
        self.destroy() 


    def _set_sidebar_buttons(self, config): 
        """ 
        Crea los botones de navegación en la barra lateral basados en la configuración. 
        """ 
        # Limpiar botones anteriores 
        for btn in self.sidebar_button_frames: 
            btn.destroy() 
        self.sidebar_button_frames.clear() 

        for i, (text, command, icon) in enumerate(config): 
            btn_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent") 
            btn_frame.grid(row=i + 1, column=0, padx=5, pady=5, sticky="ew") 
            btn_frame.grid_columnconfigure(0, weight=1)  
            
            button = customtkinter.CTkButton( 
                btn_frame,  
                text=text,  
                command=command, 
                compound="left", 
                image=icon if icon else None, 
                anchor="w" 
            ) 
            button.grid(row=0, column=0, sticky="ew", padx=10) 
            self.sidebar_button_frames.append(btn_frame) 


    def _clear_main_content(self): 
        """ 
        Destruye el contenido actual dentro de self.main_content  
        y resetea la configuración de la grilla para una nueva vista. 
        """ 
        for widget in self.main_content.winfo_children(): 
            widget.destroy() 
        
        # Resetear la configuración de columna/fila a un estado neutro
        self.main_content.grid_columnconfigure(0, weight=1) 
        self.main_content.grid_rowconfigure(0, weight=0) 
        self.main_content.grid_rowconfigure(1, weight=0)