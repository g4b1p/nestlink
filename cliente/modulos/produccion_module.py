import customtkinter
from base_module import BaseAppWindow

class ProduccionModule(BaseAppWindow):
    """Módulo de Producción (Placeholder)."""
    def __init__(self, master, user_info):
        super().__init__(master, "Producción", user_info)
        # Contenido específico del módulo Producción
        customtkinter.CTkLabel(self.main_content, text="[MÓDULO DE PRODUCCIÓN EN DESARROLLO]").pack(pady=50)