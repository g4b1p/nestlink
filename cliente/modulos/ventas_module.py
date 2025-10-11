import customtkinter
from base_module import BaseAppWindow

class VentasModule(BaseAppWindow):
    """Módulo de Ventas (Placeholder)."""
    def __init__(self, master, user_info):
        super().__init__(master, "Ventas", user_info)
        # Contenido específico del módulo Ventas
        customtkinter.CTkLabel(self.main_content, text="[MÓDULO DE VENTAS EN DESARROLLO]").pack(pady=50)