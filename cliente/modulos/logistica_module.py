import customtkinter
from base_module import BaseAppWindow

class LogisticaModule(BaseAppWindow):
    """Módulo de Logística (Placeholder)."""
    def __init__(self, master, user_info):
        super().__init__(master, "Logística", user_info)
        # Contenido específico del módulo Logística
        customtkinter.CTkLabel(self.main_content, text="[MÓDULO DE LOGÍSTICA EN DESARROLLO]").pack(pady=50)