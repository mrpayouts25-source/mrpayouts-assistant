import customtkinter as ctk
from tkinter import messagebox, simpledialog

from core.database import get_open_trades, close_trade
from core.formatter import format_result
from core.telegram import send_message


class OpenTrades(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Open Trades")
        self.geometry("1100x700")

        self.build_ui()
        self.load_trades()

    def build_ui(self):
        ctk.CTkLabel(
            self,
            text="Open Trades",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=1000,
            height=560
        )
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def load_trades(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        rows = get_open_trades()

        if not rows:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No open trades.",
                font=("Arial", 18)
            ).pack(pady=30)
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
        card = ctk.CTkFrame(self.scroll_frame)
        card.pack(fill="x", padx=20, pady=10)

        header = f"{trade['trade_number']}  |  {trade['symbol']} {trade['direction']}  |  OPEN"

        ctk.CTkLabel(
            card,
            text=header,
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))

        details = (
            f"Entry: {trade['entry']}    "
            f"SL: {trade['sl']}    "
            f"TP: {trade['tp']}    "
            f"RR: 1:{trade['rr']}"
        )

        ctk.CTkLabel(
            card,
            text=details,
            font=("Arial", 14)
        ).pack(anchor="w", padx=20, pady=5)

        buttons = ctk.CTkFrame(card)
        buttons.pack(anchor="w", padx=20, pady=(10, 15))

        ctk.CTkButton(
            buttons,
            text="TP",
            width=100,
            command=lambda: self.finish_trade(trade, "TP")
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            buttons,
            text="SL",
            width=100,
            command=lambda: self.finish_trade(trade, "SL")
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            buttons,
            text="Manual",
            width=100,
            command=lambda: self.finish_trade(trade, "MANUAL")
        ).grid(row=0, column=2, padx=5)

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

        send_message(result_message)

        messagebox.showinfo(
            "Trade Closed",
            f"Trade closed as {result} and posted to Telegram."
        )

        self.load_trades()