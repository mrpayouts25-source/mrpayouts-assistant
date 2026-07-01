import sqlite3
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from PIL import Image

from core.parser import parse_ctrader_link
from core.calculator import calculate_rr
from core.formatter import format_trade, format_result
from core.telegram import send_photo
from core.database import (
    save_trade,
    get_next_trade_number,
    get_open_trades,
    close_trade
)
from core.clipboard import paste
from core.image_generator import generate_trade_image, generate_result_image
from core.analytics import calculate_dashboard_stats
from core.charts import generate_equity_curve
from gui.components import StatCard


class Home(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("MrPayouts Assistant")
        self.geometry("1280x760")

        self.current_trade = None

        self.build_ui()

    def build_ui(self):
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self.container, width=220)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)
        self.sidebar.pack_propagate(False)

        self.main = ctk.CTkFrame(self.container)
        self.main.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        ctk.CTkLabel(self.sidebar, text="MRPAYOUTS", font=("Arial", 26, "bold")).pack(pady=(25, 5))
        ctk.CTkLabel(self.sidebar, text="Assistant", font=("Arial", 14)).pack(pady=(0, 30))

        ctk.CTkButton(self.sidebar, text="New Trade", command=self.show_new_trade).pack(fill="x", padx=20, pady=8)
        ctk.CTkButton(self.sidebar, text="Open Trades", command=self.show_open_trades).pack(fill="x", padx=20, pady=8)
        ctk.CTkButton(self.sidebar, text="History", command=self.show_history).pack(fill="x", padx=20, pady=8)
        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard).pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(self.sidebar, text="v1.4", font=("Arial", 12)).pack(side="bottom", pady=20)

        self.show_new_trade()

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_new_trade(self):
        self.clear_main()

        ctk.CTkLabel(self.main, text="New Trade", font=("Arial", 30, "bold")).pack(pady=(25, 15))

        body = ctk.CTkFrame(self.main)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        left = ctk.CTkFrame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = ctk.CTkFrame(body)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(left, text="cTrader Share Link").pack(anchor="w", padx=20, pady=(20, 5))

        link_row = ctk.CTkFrame(left)
        link_row.pack(padx=20, fill="x")

        self.link = ctk.CTkEntry(link_row, width=390)
        self.link.pack(side="left", padx=(0, 10))

        ctk.CTkButton(link_row, text="Paste", width=90, command=self.paste_link).pack(side="left")

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

        ctk.CTkLabel(right, text="Preview", font=("Arial", 22, "bold")).pack(pady=20)
        self.preview = ctk.CTkTextbox(right, width=560, height=560)
        self.preview.pack(padx=20)

    def show_open_trades(self):
        self.clear_main()

        ctk.CTkLabel(self.main, text="Open Trades", font=("Arial", 30, "bold")).pack(pady=(25, 5))
        ctk.CTkLabel(self.main, text="Manage active trades and post results").pack(pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self.main)
        scroll.pack(fill="both", expand=True, padx=25, pady=15)

        rows = get_open_trades()

        if not rows:
            ctk.CTkLabel(scroll, text="No open trades.", font=("Arial", 20, "bold")).pack(pady=60)
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

            self.create_open_trade_card(scroll, trade)

    def create_open_trade_card(self, parent, trade):
        direction = trade["direction"].upper()

        border_colour = "#22C55E" if direction == "BUY" else "#EF4444"
        badge_colour = "#14532D" if direction == "BUY" else "#7F1D1D"

        card = ctk.CTkFrame(parent, border_width=2, border_color=border_colour)
        card.pack(fill="x", padx=20, pady=12)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 8))

        ctk.CTkLabel(top, text=trade["trade_number"], font=("Arial", 22, "bold")).pack(side="left")
        ctk.CTkLabel(top, text=direction, fg_color=badge_colour, corner_radius=8, width=90, height=32).pack(side="right")

        ctk.CTkLabel(card, text=trade["symbol"], font=("Arial", 34, "bold")).pack(anchor="w", padx=20, pady=(0, 12))

        details = ctk.CTkFrame(card)
        details.pack(fill="x", padx=20, pady=(0, 15))

        self.stat(details, "Entry", trade["entry"], 0)
        self.stat(details, "SL", trade["sl"], 1)
        self.stat(details, "TP", trade["tp"], 2)
        self.stat(details, "RR", f"1:{trade['rr']}", 3)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(anchor="w", padx=20, pady=(0, 18))

        ctk.CTkButton(buttons, text="TP", width=120, fg_color="#16A34A",
                      command=lambda: self.finish_trade(trade, "TP")).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(buttons, text="SL", width=120, fg_color="#DC2626",
                      command=lambda: self.finish_trade(trade, "SL")).grid(row=0, column=1, padx=10)

        ctk.CTkButton(buttons, text="Manual", width=120,
                      command=lambda: self.finish_trade(trade, "MANUAL")).grid(row=0, column=2, padx=10)

    def stat(self, parent, label, value, column):
        box = ctk.CTkFrame(parent)
        box.grid(row=0, column=column, padx=8, pady=10, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)

        ctk.CTkLabel(box, text=label, font=("Arial", 13)).pack(pady=(10, 2))
        ctk.CTkLabel(box, text=str(value), font=("Arial", 18, "bold")).pack(pady=(0, 10))

    def show_history(self):
        self.clear_main()

        ctk.CTkLabel(self.main, text="Trade History", font=("Arial", 30, "bold")).pack(pady=(25, 5))
        ctk.CTkLabel(self.main, text="Review every trade, result and profit").pack(pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self.main)
        scroll.pack(fill="both", expand=True, padx=25, pady=15)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            trade_number,
            symbol,
            direction,
            entry,
            stop_loss,
            take_profit,
            rr,
            status,
            result,
            profit,
            reason,
            created_at,
            closed_at
        FROM trades
        ORDER BY id DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(scroll, text="No trade history yet.", font=("Arial", 20, "bold")).pack(pady=60)
            return

        for row in rows:
            trade = {
                "trade_number": row[0],
                "symbol": row[1],
                "direction": row[2],
                "entry": row[3],
                "sl": row[4],
                "tp": row[5],
                "rr": row[6],
                "status": row[7],
                "result": row[8],
                "profit": row[9],
                "reason": row[10],
                "created_at": row[11],
                "closed_at": row[12]
            }

            self.create_history_card(scroll, trade)

    def create_history_card(self, parent, trade):
        direction = str(trade["direction"]).upper()
        status = trade["status"] or "OPEN"
        result = trade["result"] or "OPEN"
        profit = trade["profit"]

        border_colour = "#22C55E" if direction == "BUY" else "#EF4444"

        if result == "TP":
            result_colour = "#22C55E"
            result_badge = "TP ✅"
        elif result == "SL":
            result_colour = "#EF4444"
            result_badge = "SL ❌"
        elif result == "MANUAL":
            result_colour = "#60A5FA"
            result_badge = "MANUAL ⚪"
        else:
            result_colour = "#94A3B8"
            result_badge = "OPEN"

        card = ctk.CTkFrame(parent, border_width=2, border_color=border_colour)
        card.pack(fill="x", padx=20, pady=12)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 8))

        ctk.CTkLabel(top, text=trade["trade_number"], font=("Arial", 22, "bold")).pack(side="left")

        ctk.CTkLabel(
            top,
            text=result_badge,
            fg_color=result_colour,
            corner_radius=8,
            width=120,
            height=32,
            font=("Arial", 14, "bold")
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=f"{trade['symbol']} {direction}",
            font=("Arial", 34, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 12))

        details = ctk.CTkFrame(card)
        details.pack(fill="x", padx=20, pady=(0, 15))

        self.stat(details, "Entry", trade["entry"], 0)
        self.stat(details, "SL", trade["sl"], 1)
        self.stat(details, "TP", trade["tp"], 2)
        self.stat(details, "RR", f"1:{trade['rr']}", 3)

        money_row = ctk.CTkFrame(card)
        money_row.pack(fill="x", padx=20, pady=(0, 15))

        profit_text = "OPEN" if profit is None else f"£{profit}"
        profit_colour = "#94A3B8"

        if profit is not None:
            profit_colour = "#22C55E" if profit >= 0 else "#EF4444"

        profit_box = ctk.CTkFrame(money_row)
        profit_box.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkLabel(profit_box, text="Profit / Loss", font=("Arial", 13)).pack(pady=(10, 2))
        ctk.CTkLabel(
            profit_box,
            text=profit_text,
            font=("Arial", 22, "bold"),
            text_color=profit_colour
        ).pack(pady=(0, 10))

        status_box = ctk.CTkFrame(money_row)
        status_box.pack(side="left", fill="x", expand=True, padx=(8, 0))

        ctk.CTkLabel(status_box, text="Status", font=("Arial", 13)).pack(pady=(10, 2))
        ctk.CTkLabel(status_box, text=status, font=("Arial", 22, "bold")).pack(pady=(0, 10))

        if trade["reason"]:
            reason_box = ctk.CTkFrame(card)
            reason_box.pack(fill="x", padx=20, pady=(0, 15))

            ctk.CTkLabel(reason_box, text="Reason", font=("Arial", 13)).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(
                reason_box,
                text=trade["reason"],
                font=("Arial", 15),
                wraplength=850,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 12))

        date_text = f"Opened: {trade['created_at']}"
        if trade["closed_at"]:
            date_text += f"   |   Closed: {trade['closed_at']}"

        ctk.CTkLabel(
            card,
            text=date_text,
            font=("Arial", 12),
            text_color="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(0, 15))

    def show_dashboard(self):
        self.clear_main()

        stats = calculate_dashboard_stats()

        ctk.CTkLabel(self.main, text="Dashboard", font=("Arial", 30, "bold")).pack(pady=(25, 15))

        scroll = ctk.CTkScrollableFrame(self.main)
        scroll.pack(fill="both", expand=True, padx=25, pady=15)

        chart_path = generate_equity_curve()
        chart_image = ctk.CTkImage(
            light_image=Image.open(chart_path),
            dark_image=Image.open(chart_path),
            size=(850, 425)
        )

        chart_label = ctk.CTkLabel(scroll, text="", image=chart_image)
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
            card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
            grid.grid_columnconfigure(column, weight=1)

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

            trade["rr"] = calculate_rr(trade["entry"], trade["sl"], trade["tp"])
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

    def finish_trade(self, trade, result):
        profit = simpledialog.askfloat(
            "Profit / Loss",
            "Enter profit or loss amount (£):"
        )

        if profit is None:
            return

        close_trade(trade["id"], result, profit)

        result_message = format_result(
            trade["trade_number"],
            trade["symbol"],
            trade["direction"],
            result,
            profit
        )

        image_path = generate_result_image(trade, result, profit)

        sent = send_photo(image_path, caption=result_message)

        if sent:
            messagebox.showinfo("Trade Closed", f"Trade closed as {result} and posted to Telegram.")
        else:
            messagebox.showerror("Error", "Trade closed, but Telegram failed.")

        self.show_open_trades()

    def clear(self):
        self.current_trade = None

        if hasattr(self, "link"):
            self.link.delete(0, "end")

        if hasattr(self, "entry"):
            self.entry.delete(0, "end")

        if hasattr(self, "reason"):
            self.reason.delete("1.0", "end")

        if hasattr(self, "preview"):
            self.preview.delete("1.0", "end")