import customtkinter
from PIL import Image
import os
import conexion_servidor

# Establecemos la apariencia y el color por defecto de CTk
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class LoginApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Configuración de la Ventana Principal ---
        self.geometry("800x500")
        self.title("Tu ERP - Iniciar Sesión")
        
        # Color estático de fondo para mimetizar los bordes de la imagen.
        self.configure(fg_color="#73a0cb")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

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
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        self.label.grid(row=1, column=0, pady=(40, 25), padx=25, sticky="ew")

        # Entrada de Usuario
        self.username_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Usuario", width=280)
        self.username_entry.grid(row=2, column=0, pady=12, padx=35, sticky="ew")

        # Entrada de Contraseña
        self.password_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Contraseña", show="*", width=280)
        self.password_entry.grid(row=3, column=0, pady=12, padx=35, sticky="ew")

        # Botón de Login
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Entrar", command=self.handle_login, width=280, height=40)
        self.login_button.grid(row=4, column=0, pady=(20, 15), padx=35, sticky="ew")

        # Etiqueta de Estado/Error
        self.status_label = customtkinter.CTkLabel(self.login_frame, text="", text_color="#FF4136", wraplength=280)
        self.status_label.grid(row=5, column=0, pady=(10, 30), padx=25)


    def handle_login(self):
        """Lógica de manejo de login (simulada)."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Simulación de respuesta 
        try:
            response = conexion_servidor.login(username, password)
            if response and "message" in response:
                if response["message"] == "Login exitoso":
                    self.status_label.configure(text="¡Login exitoso!", text_color="green")
                else:
                    self.status_label.configure(text=response["message"])
            else:
                self.status_label.configure(text="Error de conexión con el servidor.")
        except NameError:
            self.status_label.configure(text="Error: 'conexion_servidor' no está definido.")
        except Exception as e:
            self.status_label.configure(text=f"Error inesperado: {e}")


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()