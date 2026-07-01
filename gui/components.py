import customtkinter as ctk


class StatCard(ctk.CTkFrame):

    def __init__(self, master, title, value):
        super().__init__(master, corner_radius=12)

        self.configure(height=120)

        ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 15)
        ).pack(pady=(18, 5))

        ctk.CTkLabel(
            self,
            text=str(value),
            font=("Arial", 28, "bold")
        ).pack()