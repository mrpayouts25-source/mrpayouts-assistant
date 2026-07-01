import customtkinter as ctk
from tkinter import messagebox

from core.database import update_trade_notes


class TradeNotes(ctk.CTkToplevel):

    def __init__(self, master, trade_number):
        super().__init__(master)

        self.trade_number = trade_number

        self.title(f"Trade Notes {trade_number}")
        self.geometry("650x700")

        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(
            self,
            text=f"Trade Notes {self.trade_number}",
            font=("Arial", 28, "bold")
        ).pack(pady=25)

        ctk.CTkLabel(self, text="Followed Plan?").pack(anchor="w", padx=40, pady=(10, 5))
        self.followed_plan = ctk.CTkOptionMenu(self, values=["Yes", "No", "Partly"])
        self.followed_plan.pack(padx=40, fill="x")

        ctk.CTkLabel(self, text="Mistake").pack(anchor="w", padx=40, pady=(20, 5))
        self.mistake = ctk.CTkTextbox(self, height=90)
        self.mistake.pack(padx=40, fill="x")

        ctk.CTkLabel(self, text="Emotion").pack(anchor="w", padx=40, pady=(20, 5))
        self.emotion = ctk.CTkTextbox(self, height=90)
        self.emotion.pack(padx=40, fill="x")

        ctk.CTkLabel(self, text="Lesson").pack(anchor="w", padx=40, pady=(20, 5))
        self.lesson = ctk.CTkTextbox(self, height=90)
        self.lesson.pack(padx=40, fill="x")

        ctk.CTkLabel(self, text="Journal Notes").pack(anchor="w", padx=40, pady=(20, 5))
        self.journal_notes = ctk.CTkTextbox(self, height=120)
        self.journal_notes.pack(padx=40, fill="x")

        ctk.CTkButton(
            self,
            text="Save Notes",
            command=self.save_notes
        ).pack(pady=30)

    def save_notes(self):
        update_trade_notes(
            self.trade_number,
            self.followed_plan.get(),
            self.mistake.get("1.0", "end").strip(),
            self.emotion.get("1.0", "end").strip(),
            self.lesson.get("1.0", "end").strip(),
            self.journal_notes.get("1.0", "end").strip()
        )

        messagebox.showinfo("Saved", "Trade notes saved.")
        self.destroy()