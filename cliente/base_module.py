import customtkinter

# Definición del color celeste/azul vibrante
CELESTE_COLOR = "#3498DB" 

class BaseAppWindow(customtkinter.CTkToplevel):
    """Ventana base para todos los módulos de la aplicación (Dashboard)."""
    def __init__(self, master, title, user_info):
        super().__init__(master)
        self.master = master
        self.user_info = user_info
        
        self.title(f"Nestlink ERP - Módulo de {title}")
        
        # --- LÓGICA DE CENTRADO DE VENTANA ---
        window_width = 1000
        window_height = 700
        
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        # Aplicar geometría: (ancho)x(alto)+(pos_x)+(pos_y) para centrar
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}") 
        self.minsize(800, 600)
        
        self.grab_set() # Bloquea la interacción con la ventana de login
        self.master.withdraw() # Oculta la ventana de login (Master)
        
        self.protocol("WM_DELETE_WINDOW", self.logout)
        
        # Configuración de layout principal (Ahora con 2 columnas: Sidebar y Contenido)
        self.grid_rowconfigure(0, weight=1)  # Fila 0 (única) se expande
        self.grid_columnconfigure(0, weight=0) # Columna 0 (Sidebar) no se expande
        self.grid_columnconfigure(1, weight=1) # Columna 1 (Contenido principal) se expande
        
        # ------------------- 1. Barra Lateral (Sidebar) -------------------
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Espacio para empujar el logout al fondo
        
        customtkinter.CTkLabel(self.sidebar_frame, 
                               text=f"Menú de {title}", 
                               font=customtkinter.CTkFont(size=20, weight="bold"),
                               text_color=CELESTE_COLOR).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_frames = [] # Lista para guardar los botones modulares

        # Botón de cierre de sesión
        self.logout_button = customtkinter.CTkButton(self.sidebar_frame, 
                                                    text="Cerrar Sesión", 
                                                    command=self.logout, 
                                                    fg_color="#E74C3C")
        self.logout_button.grid(row=99, column=0, padx=20, pady=(10, 20), sticky="s") # Usar un row alto para que quede al fondo
        

        # ------------------- 2. Contenido Principal -------------------
        self.main_content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        
        # Contenido inicial de ejemplo
        self.main_content = customtkinter.CTkScrollableFrame(self.main_content_frame)
        self.main_content.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)

        welcome_text = f"Hola, {user_info.get('username', 'Usuario')}. Estás en el módulo de {title}."
        self.initial_label = customtkinter.CTkLabel(self.main_content, text=welcome_text, font=customtkinter.CTkFont(size=20))
        self.initial_label.pack(padx=50, pady=50)


    def logout(self):
        """Cierra la ventana actual (módulo) y vuelve a mostrar el Login."""
        self.master.deiconify() 
        self.destroy()

    # =================================================================
    # MÉTODOS AÑADIDOS PARA SOPORTAR RRHHModule
    # =================================================================
    
    def _set_sidebar_buttons(self, config):
        """
        Crea los botones de navegación en la barra lateral basados en la configuración.
        
        Args:
            config (list): Lista de tuplas (texto, comando, icono).
        """
        # Limpiar botones anteriores
        for btn in self.sidebar_button_frames:
            btn.destroy()
        self.sidebar_button_frames.clear()

        for i, (text, command, icon) in enumerate(config):
            # Usar un frame transparente para centrar el botón en la celda
            btn_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
            btn_frame.grid(row=i + 1, column=0, padx=5, pady=5, sticky="ew")
            btn_frame.grid_columnconfigure(0, weight=1) 
            
            # El botón llama al comando del módulo
            button = customtkinter.CTkButton(
                btn_frame, 
                text=text, 
                command=command,
                compound="left",
                image=icon if icon else None,
                anchor="w" # Alinea el texto/ícono a la izquierda
            )
            button.grid(row=0, column=0, sticky="ew", padx=10)
            self.sidebar_button_frames.append(btn_frame)


    def _clear_main_content(self):
        """
        Destruye el contenido actual dentro de self.main_content 
        y lo prepara para una nueva vista.
        """
        # Destruir el contenido actual del scrollable frame
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Resetear la configuración de columna/fila del scrollable frame si es necesario
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=0)
        self.main_content.grid_rowconfigure(1, weight=0)
        # Si tienes que eliminar el scrollable frame y crearlo de nuevo:
        # self.main_content.destroy()
        # self.main_content = customtkinter.CTkScrollableFrame(self.main_content_frame)
        # self.main_content.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")