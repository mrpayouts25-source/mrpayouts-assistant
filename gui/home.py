import customtkinter as ctk
from tkinter import messagebox

from core.parser import parse_ctrader_link
from core.calculator import calculate_rr
from core.formatter import format_trade
from core.telegram import send_photo
from core.database import (
    save_trade,
    get_next_trade_number
)
from core.clipboard import paste
from core.image_generator import generate_trade_image

from gui.history import History
from gui.open_trades import OpenTrades
from gui.dashboard import Dashboard


class Home(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("MrPayouts Assistant")
        self.geometry("1250x740")

        self.current_trade = None

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(
            self,
            text="MrPayouts Assistant",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        left = ctk.CTkFrame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left, text="cTrader Share Link").pack(anchor="w", padx=20, pady=(20, 5))

        link_row = ctk.CTkFrame(left)
        link_row.pack(padx=20, fill="x")

        self.link = ctk.CTkEntry(link_row, width=390)
        self.link.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            link_row,
            text="Paste",
            width=90,
            command=self.paste_link
        ).pack(side="left")

        ctk.CTkLabel(left, text="Entry").pack(anchor="w", padx=20, pady=(15, 5))

        self.entry = ctk.CTkEntry(left, width=200)
        self.entry.pack(padx=20)

        ctk.CTkLabel(left, text="Risk (%)").pack(anchor="w", padx=20, pady=(15, 5))

        self.risk = ctk.CTkEntry(left, width=200)
        self.risk.insert(0, "1")
        self.risk.pack(padx=20)

        ctk.CTkLabel(left, text="Reason").pack(anchor="w", padx=20, pady=(15, 5))

        self.reason = ctk.CTkTextbox(left, width=500, height=180)
        self.reason.pack(padx=20)

        ctk.CTkButton(left, text="Preview", command=self.preview_trade).pack(pady=(25, 10))
        ctk.CTkButton(left, text="Send To Telegram", command=self.send_trade).pack()
        ctk.CTkButton(left, text="Clear", command=self.clear).pack(pady=10)
        ctk.CTkButton(left, text="Open Trades", command=self.open_trades).pack()
        ctk.CTkButton(left, text="History", command=self.open_history).pack(pady=10)
        ctk.CTkButton(left, text="Dashboard", command=self.open_dashboard).pack()

        right = ctk.CTkFrame(body)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            right,
            text="Preview",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        self.preview = ctk.CTkTextbox(right, width=560, height=560)
        self.preview.pack(padx=20)

    def paste_link(self):
        self.link.delete(0, "end")
        self.link.insert(0, paste())

    def preview_trade(self):
        try:
            parsed = parse_ctrader_link(self.link.get().strip())

            trade = {
                "trade_number": get_next_trade_number(),
                "symbol": parsed["symbol"],
                "direction": parsed["direction"],
                "entry": float(self.entry.get()),
                "sl": parsed["sl"],
                "tp": parsed["tp"],
                "risk": float(self.risk.get()),
                "reason": self.reason.get("1.0", "end").strip()
            }

            trade["rr"] = calculate_rr(
                trade["entry"],
                trade["sl"],
                trade["tp"]
            )

            trade["message"] = format_trade(trade)
            self.current_trade = trade

            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", trade["message"])

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_trade(self):
        if self.current_trade is None:
            messagebox.showwarning("Warning", "Preview a trade first.")
            return

        try:
            image_path = generate_trade_image(self.current_trade)

            sent = send_photo(
                image_path,
                caption=self.current_trade["message"]
            )

            if sent:
                save_trade(self.current_trade)
                messagebox.showinfo("Success", "Trade image posted.")
                self.clear()
            else:
                messagebox.showerror("Error", "Telegram failed.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_history(self):
        History(self)

    def open_trades(self):
        OpenTrades(self)

    def open_dashboard(self):
        Dashboard(self)

    def clear(self):
        self.current_trade = None
        self.link.delete(0, "end")
        self.entry.delete(0, "end")
        self.reason.delete("1.0", "end")
        self.preview.delete("1.0", "end")