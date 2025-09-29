import customtkinter
from PIL import Image
import os
import conexion_servidor

# --- CONFIGURACIÓN GLOBAL ---
# Establecemos la apariencia y el color por defecto de CTk
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Definición del color celeste/azul vibrante para la aplicación
CELESTE_COLOR = "#3498DB" 


# =================================================================
# 1. VENTANA PRINCIPAL - LOGIN
# =================================================================

class LoginApp(customtkinter.CTk):
    """Ventana principal de la aplicación, utilizada para el inicio de sesión."""
    def __init__(self):
        super().__init__()

        # --- 1. Configuración de la Ventana Principal ---
        self.geometry("800x500")
        self.title("Nestlink ERP - Iniciar Sesión")
        
        # Color estático de fondo para mimetizar los bordes de la imagen.
        self.configure(fg_color="#73a0cb")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.module_window = None 

        # --- 2. Implementación de la Imagen de Fondo ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "images", "login-img.png")
        
        try:
            self.bg_image_original = Image.open(image_path)
            self.bg_image_ctk = customtkinter.CTkImage(
                light_image=self.bg_image_original, 
                dark_image=self.bg_image_original, 
                size=(1, 1) 
            )

            self.bg_label = customtkinter.CTkLabel(
                self, 
                image=self.bg_image_ctk, 
                text="" 
            )
            
            # La imagen se ancla a la parte superior y se expande.
            self.bg_label.grid(row=0, column=0, sticky="new") 
            self.bind("<Configure>", self._resize_image)

        except FileNotFoundError:
            print(f"Error: No se encontró la imagen en la ruta: {image_path}")
            self.bg_label = customtkinter.CTkLabel(self, text="Fondo no disponible", fg_color="gray", text_color="white")
            self.bg_label.grid(row=0, column=0, sticky="nsew")

        # --- 3. Llamada al Panel de Login ---
        self.create_login_panel()
        self.after(100, lambda: self._resize_image(None))


    def _resize_image(self, event):
        """
        Redimensiona la imagen de fondo para el modo 'contain' (ver completa) 
        y la alinea a la cima, manteniendo el aspecto ratio.
        """
        if hasattr(self, 'bg_image_ctk') and hasattr(self, 'bg_image_original'):
            new_width = self.winfo_width() if event is None else event.width
            new_height = self.winfo_height() if event is None else event.height
            
            if new_width <= 0 or new_height <= 0:
                return
            
            original_width, original_height = self.bg_image_original.size
            
            width_ratio = new_width / original_width
            height_ratio = new_height / original_height
            
            # Modo 'contain' (el más pequeño factor de escala)
            scale_factor = min(width_ratio, height_ratio)
            
            new_image_width = int(original_width * scale_factor)
            new_image_height = int(original_height * scale_factor)

            if new_image_width == 0:
                new_image_width = 1
            if new_image_height == 0:
                new_image_height = 1

            self.bg_image_ctk.configure(size=(new_image_width, new_image_height))


    def create_login_panel(self):
        """
        Crea el marco del formulario y lo posiciona en la parte derecha de la ventana.
        """
        # --- Configuración del Marco de Login ---
        self.login_frame = customtkinter.CTkFrame(
            self, 
            width=350, 
            height=400, 
            corner_radius=30, 
            # Soporte de tema Claro/Oscuro
            fg_color=("white", "gray17"), 
            border_width=2, 
            border_color=("gray80", "gray25") 
        )
        
        # Posicionamiento: centrado verticalmente y movido a la izquierda (relx=0.70).
        self.login_frame.place(relx=0.70, rely=0.5, anchor="center") 
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        # --- Widgets dentro del Marco ---
        
        # Título 
        self.label = customtkinter.CTkLabel(
            self.login_frame, 
            text="Inicio de Sesión", 
            text_color=(CELESTE_COLOR, "white"), 
            font=customtkinter.CTkFont(size=28, weight="bold")
        )
        self.label.grid(row=0, column=0, pady=(40, 15), padx=35, sticky="ew") 

        # Etiqueta de Usuario
        self.username_label = customtkinter.CTkLabel(
            self.login_frame, 
            text="Usuario", 
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=(CELESTE_COLOR, CELESTE_COLOR)
        )
        self.username_label.grid(row=1, column=0, padx=35, sticky="w") 

        # Entrada de Usuario
        self.username_entry = customtkinter.CTkEntry(
            self.login_frame, 
            placeholder_text="Ingrese su usuario", 
            width=280,
            height=40, 
            corner_radius=20, 
            border_color=CELESTE_COLOR 
        )
        self.username_entry.grid(row=2, column=0, pady=(0, 20), padx=35, sticky="ew") 

        # Etiqueta de Contraseña
        self.password_label = customtkinter.CTkLabel(
            self.login_frame, 
            text="Contraseña", 
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=(CELESTE_COLOR, CELESTE_COLOR)
        )
        self.password_label.grid(row=3, column=0, padx=35, sticky="w") 

        # Entrada de Contraseña
        self.password_entry = customtkinter.CTkEntry(
            self.login_frame, 
            placeholder_text="Ingrese su contraseña", 
            show="*", 
            width=280,
            height=40, 
            corner_radius=20, 
            border_color=CELESTE_COLOR 
        )
        self.password_entry.grid(row=4, column=0, pady=(0, 20), padx=35, sticky="ew") 

        # Botón de Login 
        self.login_button = customtkinter.CTkButton(
            self.login_frame, 
            text="Entrar", 
            command=self.handle_login, 
            width=280, 
            height=45,
            corner_radius=20,
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        self.login_button.grid(row=5, column=0, pady=(10, 15), padx=35, sticky="ew") 

        # Etiqueta de Estado/Error
        self.status_label = customtkinter.CTkLabel(self.login_frame, text="", text_color="#FF4136", wraplength=280)
        self.status_label.grid(row=6, column=0, pady=(10, 30), padx=25) 


    def handle_login(self):
        """Lógica de manejo de login y redirección modular."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        try:
            # Llama a la función de conexión para simular la autenticación
            response = conexion_servidor.login(username, password)
            if response and "message" in response:
                if response["message"] == "Login exitoso":
                    self.status_label.configure(text="¡Login exitoso! Abriendo módulo...", text_color="green")
                    
                    # Obtiene el rol (sector) del usuario
                    user_role = response.get('role', 'Desconocido') 
                    
                    # Navegación al módulo correspondiente
                    self.open_module_window(response, user_role)
                    
                else:
                    self.status_label.configure(text=response["message"])
            else:
                self.status_label.configure(text="Error desconocido de conexión.")
        
        except Exception as e:
            print(f"Error en handle_login: {e}")
            self.status_label.configure(text=f"Error inesperado al conectar.", text_color="red")

    
    def open_module_window(self, user_info, role):
        """Abre la ventana del módulo basado en el rol."""
        
        # Mapeo del rol a la clase de la ventana del módulo
        module_map = {
            'RRHH': RRHHModule,
            'VENTAS': VentasModule,
            'MARKETING': MarketingModule,
            'LOGISTICA': LogisticaModule,
            'PRODUCCION': ProduccionModule
        }
        
        normalized_role = role.upper()
        ModuleClass = module_map.get(normalized_role)

        if ModuleClass:
            # Destruye el módulo anterior si existe
            if self.module_window and self.module_window.winfo_exists():
                self.module_window.destroy()
                
            self.module_window = ModuleClass(self, user_info)
        else:
            self.status_label.configure(text=f"Error: Rol '{role}' no soportado por la aplicación. Roles válidos: {list(module_map.keys())}", text_color="red")


# =================================================================
# 2. CLASE BASE DE MÓDULOS DE APLICACIÓN 
# =================================================================

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
        
        # Configuración de layout principal
        self.grid_rowconfigure(1, weight=1)  
        self.grid_columnconfigure(0, weight=1)
        
        # ------------------- Header (Título y Botón de Logout) -------------------
        header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = customtkinter.CTkLabel(header_frame, 
                                            text=f"MÓDULO DE {title.upper()}", 
                                            font=customtkinter.CTkFont(size=32, weight="bold"),
                                            text_color=CELESTE_COLOR)
        title_label.grid(row=0, column=0, padx=20, sticky="w")
        
        # Botón de cierre de sesión
        self.logout_button = customtkinter.CTkButton(header_frame, 
                                                    text="Cerrar Sesión", 
                                                    command=self.logout, 
                                                    fg_color="#E74C3C")
        self.logout_button.grid(row=0, column=1, padx=20, sticky="e")
        

        # ------------------- Contenido Principal (Scrollable Frame) -------------------
        self.main_content = customtkinter.CTkScrollableFrame(self)
        self.main_content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Contenido inicial de ejemplo 
        welcome_text = f"Hola, {user_info.get('username', 'Usuario')}. Estás en el módulo de {title}."
        customtkinter.CTkLabel(self.main_content, text=welcome_text, font=customtkinter.CTkFont(size=20)).pack(padx=50, pady=50)


    def logout(self):
        """Cierra la ventana actual (módulo) y vuelve a mostrar el Login."""
        self.master.deiconify() 
        self.destroy() 


# =================================================================
# 3. CLASES ESPECÍFICAS POR MÓDULO
# =================================================================

class RRHHModule(BaseAppWindow):
    """Módulo para Recursos Humanos."""
    def __init__(self, master, user_info):
        super().__init__(master, "Recursos Humanos", user_info)
        # Contenido específico del módulo RRHH
        customtkinter.CTkLabel(self.main_content, text="Panel de Gestión de Empleados y Nóminas").pack(pady=20)

class VentasModule(BaseAppWindow):
    """Módulo para Ventas."""
    def __init__(self, master, user_info):
        super().__init__(master, "Ventas", user_info)
        # Contenido específico del módulo Ventas
        customtkinter.CTkLabel(self.main_content, text="Panel de Pedidos y Clientes").pack(pady=20)

class MarketingModule(BaseAppWindow):
    """Módulo para Marketing."""
    def __init__(self, master, user_info):
        super().__init__(master, "Marketing", user_info)
        # Contenido específico del módulo Marketing
        customtkinter.CTkLabel(self.main_content, text="Panel de Campañas y Análisis").pack(pady=20)
        
class LogisticaModule(BaseAppWindow):
    """Módulo para Logística."""
    def __init__(self, master, user_info):
        super().__init__(master, "Logística", user_info)
        # Contenido específico del módulo Logística
        customtkinter.CTkLabel(self.main_content, text="Panel de Almacenes y Envíos").pack(pady=20)

class ProduccionModule(BaseAppWindow):
    """Módulo para Producción."""
    def __init__(self, master, user_info):
        super().__init__(master, "Producción", user_info)
        # Contenido específico del módulo Producción
        customtkinter.CTkLabel(self.main_content, text="Panel de Órdenes de Producción y Materiales").pack(pady=20)


# =================================================================
# INICIO DE LA APLICACIÓN
# =================================================================

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()