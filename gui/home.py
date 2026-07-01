import customtkinter as ctk

from gui.pages.new_trade import NewTradePage
from gui.pages.open_trades import OpenTradesPage
from gui.pages.history import HistoryPage
from gui.pages.dashboard import DashboardPage


class Home(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("MrPayouts Assistant")
        self.geometry("1280x760")

        self.build_ui()

    def build_ui(self):
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self.container, width=220)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)
        self.sidebar.pack_propagate(False)

        self.main = ctk.CTkFrame(self.container)
        self.main.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        ctk.CTkLabel(
            self.sidebar,
            text="MRPAYOUTS",
            font=("Arial", 26, "bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="Assistant",
            font=("Arial", 14)
        ).pack(pady=(0, 30))

        ctk.CTkButton(
            self.sidebar,
            text="New Trade",
            command=self.show_new_trade
        ).pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(
            self.sidebar,
            text="Open Trades",
            command=self.show_open_trades
        ).pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(
            self.sidebar,
            text="History",
            command=self.show_history
        ).pack(fill="x", padx=20, pady=8)

        ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=self.show_dashboard
        ).pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            self.sidebar,
            text="v1.7",
            font=("Arial", 12)
        ).pack(side="bottom", pady=20)

        self.show_new_trade()

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def load_page(self, page_class):
        self.clear_main()
        page = page_class(self.main)
        page.pack(fill="both", expand=True)

    def show_new_trade(self):
        self.load_page(NewTradePage)

    def show_open_trades(self):
        self.load_page(OpenTradesPage)

    def show_history(self):
        self.load_page(HistoryPage)

    def show_dashboard(self):
        self.load_page(DashboardPage)