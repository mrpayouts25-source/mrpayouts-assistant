import customtkinter as ctk
import sqlite3


class History(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Trade History")
        self.geometry("1100x650")

        self.build_ui()

        self.load_trades()

    def build_ui(self):

        title = ctk.CTkLabel(

            self,

            text="Trade History",

            font=("Arial", 28, "bold")

        )

        title.pack(pady=20)

        self.table = ctk.CTkTextbox(

            self,

            width=1000,

            height=520

        )

        self.table.pack(padx=20, pady=20)

    def load_trades(self):

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

        created_at

        FROM trades

        ORDER BY id DESC

        """)

        rows = cursor.fetchall()

        conn.close()

        self.table.delete("1.0", "end")

        self.table.insert(

            "end",

            "Trade | Symbol | Dir | Entry | SL | TP | RR | Status | Date\n"

        )

        self.table.insert(

            "end",

            "-" * 120 + "\n"

        )

        for row in rows:

            self.table.insert(

                "end",

                f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]}\n"

            )