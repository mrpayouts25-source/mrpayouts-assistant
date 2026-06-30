import customtkinter as ctk
import sqlite3


class Dashboard(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Dashboard")
        self.geometry("750x600")

        self.build_ui()

    def build_ui(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM trades WHERE status='OPEN'")
        open_trades = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM trades WHERE result='TP'")
        wins = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM trades WHERE result='SL'")
        losses = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(profit), 0) FROM trades")
        net_profit = cursor.fetchone()[0]

        conn.close()

        if wins + losses > 0:
            win_rate = round((wins / (wins + losses)) * 100, 2)
        else:
            win_rate = 0

        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 30, "bold")
        ).pack(pady=25)

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        stats = [
            ("Total Trades", total_trades),
            ("Open Trades", open_trades),
            ("Wins", wins),
            ("Losses", losses),
            ("Win Rate", f"{win_rate}%"),
            ("Net Profit", f"£{net_profit:.2f}")
        ]

        for title, value in stats:
            card = ctk.CTkFrame(frame)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 16)
            ).pack(pady=(12, 3))

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 26, "bold")
            ).pack(pady=(0, 12))