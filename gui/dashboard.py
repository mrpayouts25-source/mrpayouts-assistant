import customtkinter as ctk
from PIL import Image

from core.analytics import calculate_dashboard_stats
from core.charts import generate_equity_curve


class Dashboard(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Dashboard")
        self.geometry("1000x800")

        self.build_ui()

    def build_ui(self):
        stats = calculate_dashboard_stats()

        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 30, "bold")
        ).pack(pady=20)

        frame = ctk.CTkScrollableFrame(self, width=930, height=720)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        chart_path = generate_equity_curve()
        chart_image = ctk.CTkImage(
            light_image=Image.open(chart_path),
            dark_image=Image.open(chart_path),
            size=(850, 425)
        )

        chart_label = ctk.CTkLabel(
            frame,
            text="",
            image=chart_image
        )
        chart_label.pack(pady=(10, 25))

        stat_items = [
            ("Closed Trades", stats["total_closed"]),
            ("Wins", stats["wins"]),
            ("Losses", stats["losses"]),
            ("Win Rate", f"{stats['win_rate']}%"),
            ("Total Profit", f"£{stats['total_profit']}"),
            ("Average Win", f"£{stats['average_win']}"),
            ("Average Loss", f"£{stats['average_loss']}"),
            ("Largest Win", f"£{stats['largest_win']}"),
            ("Largest Loss", f"£{stats['largest_loss']}"),
            ("Profit Factor", stats["profit_factor"]),
            ("Average RR", f"1:{stats['average_rr']}"),
            ("Expectancy", f"£{stats['expectancy']}"),
        ]

        for title, value in stat_items:
            card = ctk.CTkFrame(frame)
            card.pack(fill="x", pady=8, padx=10)

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