import customtkinter as ctk
from PIL import Image

from core.analytics import calculate_dashboard_stats
from core.charts import generate_equity_curve
from gui.components import StatCard


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.build_ui()

    def build_ui(self):
        stats = calculate_dashboard_stats()

        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 30, "bold")
        ).pack(pady=(25, 15))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=25, pady=15)

        chart_path = generate_equity_curve()

        chart_image = ctk.CTkImage(
            light_image=Image.open(chart_path),
            dark_image=Image.open(chart_path),
            size=(850, 425)
        )

        chart_label = ctk.CTkLabel(
            scroll,
            text="",
            image=chart_image
        )
        chart_label.pack(pady=(10, 25))

        grid = ctk.CTkFrame(scroll)
        grid.pack(fill="x", padx=20, pady=20)

        stat_items = [
            ("Win Rate", f"{stats['win_rate']}%"),
            ("Total P/L", f"£{stats['total_profit']}"),
            ("Average RR", f"1:{stats['average_rr']}"),
            ("Closed Trades", stats["total_closed"]),
            ("Wins", stats["wins"]),
            ("Losses", stats["losses"]),
            ("Average Win", f"£{stats['average_win']}"),
            ("Average Loss", f"£{stats['average_loss']}"),
            ("Profit Factor", stats["profit_factor"]),
            ("Expectancy", f"£{stats['expectancy']}"),
            ("Largest Win", f"£{stats['largest_win']}"),
            ("Largest Loss", f"£{stats['largest_loss']}"),
        ]

        for index, (title, value) in enumerate(stat_items):
            row = index // 3
            column = index % 3

            card = StatCard(grid, title, value)
            card.grid(
                row=row,
                column=column,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            grid.grid_columnconfigure(column, weight=1)