import customtkinter
from base_module import BaseAppWindow

class MarketingModule(BaseAppWindow):
    """Módulo de Marketing (Placeholder)."""
    def __init__(self, master, user_info):
        super().__init__(master, "Marketing", user_info)
        # Contenido específico del módulo Marketing
        customtkinter.CTkLabel(self.main_content, text="[MÓDULO DE MARKETING EN DESARROLLO]").pack(pady=50)