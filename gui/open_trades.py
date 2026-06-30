import customtkinter as ctk
from tkinter import messagebox, simpledialog

from core.database import get_open_trades, close_trade
from core.formatter import format_result
from core.telegram import send_photo
from core.image_generator import generate_result_image


class OpenTrades(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Open Trades")
        self.geometry("1150x720")

        self.build_ui()
        self.load_trades()

    def build_ui(self):
        ctk.CTkLabel(
            self,
            text="Open Trades",
            font=("Arial", 30, "bold")
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            self,
            text="Manage active trades and post results",
            font=("Arial", 14)
        ).pack(pady=(0, 15))

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=1050,
            height=580
        )
        self.scroll_frame.pack(padx=25, pady=10, fill="both", expand=True)

    def load_trades(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        rows = get_open_trades()

        if not rows:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No open trades.",
                font=("Arial", 20, "bold")
            ).pack(pady=60)
            return

        for row in rows:
            trade = {
                "id": row[0],
                "trade_number": row[1],
                "symbol": row[2],
                "direction": row[3],
                "entry": row[4],
                "sl": row[5],
                "tp": row[6],
                "rr": row[7],
                "created_at": row[8]
            }

            self.create_trade_card(trade)

    def create_trade_card(self, trade):
        direction = trade["direction"].upper()

        border_colour = "#22C55E" if direction == "BUY" else "#EF4444"
        badge_colour = "#14532D" if direction == "BUY" else "#7F1D1D"

        card = ctk.CTkFrame(
            self.scroll_frame,
            border_width=2,
            border_color=border_colour
        )
        card.pack(fill="x", padx=20, pady=12)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(18, 8))

        ctk.CTkLabel(
            top_row,
            text=trade["trade_number"],
            font=("Arial", 22, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            top_row,
            text=direction,
            font=("Arial", 16, "bold"),
            fg_color=badge_colour,
            corner_radius=8,
            width=90,
            height=32
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=trade["symbol"],
            font=("Arial", 34, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 12))

        details = ctk.CTkFrame(card)
        details.pack(fill="x", padx=20, pady=(0, 15))

        self.stat(details, "Entry", trade["entry"], 0)
        self.stat(details, "SL", trade["sl"], 1)
        self.stat(details, "TP", trade["tp"], 2)
        self.stat(details, "RR", f"1:{trade['rr']}", 3)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(anchor="w", padx=20, pady=(0, 18))

        ctk.CTkButton(
            buttons,
            text="TP",
            width=120,
            fg_color="#16A34A",
            hover_color="#15803D",
            command=lambda: self.finish_trade(trade, "TP")
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            buttons,
            text="SL",
            width=120,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda: self.finish_trade(trade, "SL")
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            buttons,
            text="Manual",
            width=120,
            command=lambda: self.finish_trade(trade, "MANUAL")
        ).grid(row=0, column=2, padx=10)

    def stat(self, parent, label, value, column):
        box = ctk.CTkFrame(parent)
        box.grid(row=0, column=column, padx=8, pady=10, sticky="nsew")

        parent.grid_columnconfigure(column, weight=1)

        ctk.CTkLabel(
            box,
            text=label,
            font=("Arial", 13)
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            box,
            text=str(value),
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))

    def finish_trade(self, trade, result):
        profit = simpledialog.askfloat(
            "Profit / Loss",
            "Enter profit or loss amount (£):"
        )

        if profit is None:
            return

        close_trade(
            trade["id"],
            result,
            profit
        )

        result_message = format_result(
            trade["trade_number"],
            trade["symbol"],
            trade["direction"],
            result,
            profit
        )

        image_path = generate_result_image(
            trade,
            result,
            profit
        )

        sent = send_photo(
            image_path,
            caption=result_message
        )

        if sent:
            messagebox.showinfo(
                "Trade Closed",
                f"Trade closed as {result} and posted to Telegram."
            )
        else:
            messagebox.showerror(
                "Error",
                "Trade closed, but Telegram failed."
            )

        self.load_trades()