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

    plt.figure(figsize=(8, 4))

    if equity:
        plt.plot(range(1, len(equity) + 1), equity, marker="o")
    else:
        plt.plot([0], [0], marker="o")

    plt.title("Equity Curve")
    plt.xlabel("Closed Trades")
    plt.ylabel("Profit (£)")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path