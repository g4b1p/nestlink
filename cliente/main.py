import customtkinter

# Crea una clase para la ventana principal de la aplicación.
class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configura la ventana principal.
        self.title("Nestlink App")
        self.geometry("500x300")

        # Crea y muestra un mensaje de bienvenida.
        welcome_label = customtkinter.CTkLabel(
            self, 
            text="Bienvenido a Nestlink", 
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        welcome_label.pack(pady=50)


if __name__ == "__main__":
    # Inicia la aplicación.
    app = MainApp()
    app.mainloop()