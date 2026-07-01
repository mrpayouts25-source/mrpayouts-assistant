import sqlite3
import customtkinter as ctk

from gui.trade_notes import TradeNotes


class HistoryPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(
            self,
            text="Trade History",
            font=("Arial", 30, "bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self,
            text="Review every trade, result and profit"
        ).pack(pady=(0, 15))

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=25, pady=15)

        self.load_history()

    def load_history(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

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
            ctk.CTkLabel(
                self.scroll,
                text="No trade history yet.",
                font=("Arial", 20, "bold")
            ).pack(pady=60)
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

            self.create_history_card(trade)

    def create_history_card(self, trade):
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

        card = ctk.CTkFrame(
            self.scroll,
            border_width=2,
            border_color=border_colour
        )
        card.pack(fill="x", padx=20, pady=12)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 8))

        ctk.CTkLabel(
            top,
            text=trade["trade_number"],
            font=("Arial", 22, "bold")
        ).pack(side="left")

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

        ctk.CTkLabel(
            profit_box,
            text="Profit / Loss",
            font=("Arial", 13)
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            profit_box,
            text=profit_text,
            font=("Arial", 22, "bold"),
            text_color=profit_colour
        ).pack(pady=(0, 10))

        status_box = ctk.CTkFrame(money_row)
        status_box.pack(side="left", fill="x", expand=True, padx=(8, 0))

        ctk.CTkLabel(
            status_box,
            text="Status",
            font=("Arial", 13)
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            status_box,
            text=status,
            font=("Arial", 22, "bold")
        ).pack(pady=(0, 10))

        if trade["reason"]:
            reason_box = ctk.CTkFrame(card)
            reason_box.pack(fill="x", padx=20, pady=(0, 15))

            ctk.CTkLabel(
                reason_box,
                text="Reason",
                font=("Arial", 13)
            ).pack(anchor="w", padx=15, pady=(10, 2))

            ctk.CTkLabel(
                reason_box,
                text=trade["reason"],
                font=("Arial", 15),
                wraplength=850,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 12))

        ctk.CTkButton(
            card,
            text="Add / Edit Notes",
            command=lambda: TradeNotes(self, trade["trade_number"])
        ).pack(anchor="w", padx=20, pady=(0, 15))

        date_text = f"Opened: {trade['created_at']}"

        if trade["closed_at"]:
            date_text += f"   |   Closed: {trade['closed_at']}"

        ctk.CTkLabel(
            card,
            text=date_text,
            font=("Arial", 12),
            text_color="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(0, 15))

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