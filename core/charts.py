import sqlite3
import os
import matplotlib.pyplot as plt

DB_NAME = "database.db"


def get_equity_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT profit
    FROM trades
    WHERE status='CLOSED'
    ORDER BY closed_at ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    equity = []
    running_total = 0

    for row in rows:
        profit = row[0] or 0
        running_total += profit
        equity.append(running_total)

    return equity


def generate_equity_curve():
    equity = get_equity_data()

    os.makedirs("data/exports", exist_ok=True)

    path = "data/exports/equity_curve.png"

    bg = "#080B12"
    panel = "#121826"
    line = "#22C55E"
    text = "#F8FAFC"
    grid = "#334155"

    plt.figure(figsize=(10, 5), facecolor=bg)
    ax = plt.axes()
    ax.set_facecolor(panel)

    if equity:
        ax.plot(
            range(1, len(equity) + 1),
            equity,
            marker="o",
            linewidth=3,
            color=line
        )
    else:
        ax.plot([0], [0], marker="o", color=line)

    ax.set_title("Equity Curve", color=text, fontsize=18, fontweight="bold")
    ax.set_xlabel("Closed Trades", color=text)
    ax.set_ylabel("Profit (£)", color=text)

    ax.tick_params(colors=text)

    for spine in ax.spines.values():
        spine.set_color(grid)

    ax.grid(True, color=grid, alpha=0.35)

    plt.tight_layout()
    plt.savefig(path, facecolor=bg)
    plt.close()

    return path