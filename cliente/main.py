import customtkinter
import conexion_servidor

class LoginApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("400x250")
        self.title("Tu ERP - Iniciar Sesión")
        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Inicio de Sesión", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, pady=10)

        self.username_entry = customtkinter.CTkEntry(self, placeholder_text="Usuario")
        self.username_entry.grid(row=1, column=0, pady=5)

        self.password_entry = customtkinter.CTkEntry(self, placeholder_text="Contraseña", show="*")
        self.password_entry.grid(row=2, column=0, pady=5)

        self.login_button = customtkinter.CTkButton(self, text="Entrar", command=self.handle_login)
        self.login_button.grid(row=3, column=0, pady=10)

        self.status_label = customtkinter.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=4, column=0, pady=5)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        response = conexion_servidor.login(username, password)
        
        if response and "message" in response:
            if response["message"] == "Login exitoso":
                self.status_label.configure(text="¡Login exitoso!", text_color="green")
                # Aquí iría el código para abrir la ventana principal de la aplicación.
            else:
                self.status_label.configure(text=response["message"])
        else:
            self.status_label.configure(text="Error de conexión con el servidor.")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()