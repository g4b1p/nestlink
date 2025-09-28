import customtkinter
from PIL import Image
import os
import conexion_servidor # Asumo que esta librería existe y maneja la lógica de conexión

# Establecemos la apariencia y el color por defecto de CTk
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class LoginApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Configuración de la Ventana ---
        # Aumentamos el tamaño para simular el layout del mockup
        self.geometry("800x500")
        self.title("Tu ERP - Iniciar Sesión")
        
        # Hacemos que la única columna y fila se expandan para que el fondo lo cubra todo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 2. Implementación de la Imagen de Fondo (bg_label) ---
        
        # Creamos la ruta completa a la imagen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "images", "login-img.png")
        
        try:
            # Cargamos la imagen original
            self.bg_image_original = Image.open(image_path)
            
            # Inicializamos CTkImage con un tamaño que se ajustará dinámicamente
            self.bg_image_ctk = customtkinter.CTkImage(
                light_image=self.bg_image_original, 
                dark_image=self.bg_image_original, 
                size=(1, 1) # Tamaño inicial temporal, se ajustará con _resize_image
            )

            # Creamos una etiqueta (Label) que contendrá la imagen de fondo
            self.bg_label = customtkinter.CTkLabel(
                self, 
                image=self.bg_image_ctk, 
                text="" 
                # La etiqueta usará automáticamente el color de fondo de la aplicación.
            )
            
            # Colocamos la etiqueta en la celda 0,0 y la expandimos horizontalmente 
            # y la pegamos al límite superior (norte).
            self.bg_label.grid(row=0, column=0, sticky="new") 
            
            # Configuramos un evento para redimensionar la imagen cuando se redimensiona la ventana
            self.bind("<Configure>", self._resize_image)

        except FileNotFoundError:
            print(f"Error: No se encontró la imagen en la ruta: {image_path}")
            # Si la imagen falla, creamos una etiqueta simple de fondo con un color
            self.bg_label = customtkinter.CTkLabel(self, text="Fondo no disponible", fg_color="gray", text_color="white")
            self.bg_label.grid(row=0, column=0, sticky="nsew")

        # --- 3. El contenido del Login (temporalmente deshabilitado/oculto) ---
        # Dejo la llamada a la función para simular el proceso de login
        self.username_entry = customtkinter.CTkEntry(self, placeholder_text="Usuario")
        self.password_entry = customtkinter.CTkEntry(self, placeholder_text="Contraseña", show="*")
        self.status_label = customtkinter.CTkLabel(self, text="", text_color="red")
        
        # Llamamos al método que creará el panel de login en el siguiente paso
        # Llamamos a _resize_image una vez al inicio para que la imagen se cargue con el tamaño correcto
        self.after(100, lambda: self._resize_image(None)) # Usamos after para asegurar que winfo_width/height sea correcto
        self.create_login_panel()


    def _resize_image(self, event):
        """
        Redimensiona la imagen de fondo para que se AJUSTE (contain), 
        mostrando la imagen completa sin salirse de los límites de la app.
        """
        if hasattr(self, 'bg_image_ctk') and hasattr(self, 'bg_image_original'):
            # 1. Dimensiones de la ventana (el contenedor de la imagen)
            new_width = self.winfo_width() if event is None else event.width
            new_height = self.winfo_height() if event is None else event.height
            
            if new_width <= 0 or new_height <= 0:
                return
            
            # 2. Dimensiones originales de la imagen
            original_width, original_height = self.bg_image_original.size
            
            # 3. Calcular los factores de escala
            width_ratio = new_width / original_width
            height_ratio = new_height / original_height
            
            # 4. Elegir el factor de escala MÁS PEQUEÑO (efecto 'contain' / "alejar al límite")
            # Esto asegura que la imagen quepa completamente, sin recorte.
            scale_factor = min(width_ratio, height_ratio)
            
            # 5. Calcular las nuevas dimensiones manteniendo el aspecto
            new_image_width = int(original_width * scale_factor)
            new_image_height = int(original_height * scale_factor)

            # 6. Reconfigurar la imagen de CTkImage
            self.bg_image_ctk.configure(size=(new_image_width, new_image_height))


    def create_login_panel(self):
        """Este método se desarrollará en el siguiente paso para añadir el formulario."""
        pass # Placeholder for the next step


    def handle_login(self):
        """Simulación de la lógica de login."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Simulación de respuesta (se requiere 'conexion_servidor' real)
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