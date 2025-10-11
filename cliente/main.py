import customtkinter
from PIL import Image
from tkinter import messagebox
import os

# =================================================================
# 1. IMPORTACIONES MODULARES (Ajustadas a tu estructura de carpetas)
# =================================================================

# Importamos las clases de módulo desde la carpeta 'modulos'
from modulos.rrhh_module import RRHHModule 
from modulos.ventas_module import VentasModule 
from modulos.marketing_module import MarketingModule 
from modulos.logistica_module import LogisticaModule 
from modulos.produccion_module import ProduccionModule 

import conexion_servidor

# --- CONFIGURACIÓN GLOBAL ---
customtkinter.set_appearance_mode("Light") 
customtkinter.set_default_color_theme("blue")
CELESTE_COLOR = "#3498DB" 


# =================================================================
# 2. VENTANA PRINCIPAL - LOGIN (Sin Cambios)
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
                    
                    # Usa after(100) para asegurar que el status_label se actualice antes de cambiar de ventana
                    self.after(100, lambda: self.open_module_window(response, user_role))
                    
                else:
                    self.status_label.configure(text=response["message"], text_color="#FF4136")
            else:
                self.status_label.configure(text="Error: Respuesta de conexión inválida.", text_color="#FF4136")
        
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor de autenticación. Detalle: {e}")
            self.status_label.configure(text="Error de conexión.", text_color="red")

    
    def open_module_window(self, user_info, role):
        """Abre la ventana del módulo basado en el rol."""
        
        # Mapeo del rol a la clase de la ventana del módulo
        module_map = {
            # Las clases son importadas al inicio del archivo
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
                
            # Instancia y abre la ventana del módulo (Pasa el login como master y la info del usuario)
            self.module_window = ModuleClass(self, user_info)
        else:
            messagebox.showerror("Error de Permisos", f"Rol '{role}' no soportado o no tiene permisos de acceso.")
            self.status_label.configure(text=f"Error: Rol '{role}' no soportado.", text_color="red")


# =================================================================
# 3. INICIO DE LA APLICACIÓN
# =================================================================

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()