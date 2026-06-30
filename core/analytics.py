import sqlite3

DB_NAME = "database.db"


def fetch_closed_trades():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        symbol,
        direction,
        rr,
        result,
        profit,
        created_at,
        closed_at
    FROM trades
    WHERE status='CLOSED'
    ORDER BY closed_at ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def calculate_dashboard_stats():
    rows = fetch_closed_trades()

    total_closed = len(rows)

    wins = [r for r in rows if r[3] == "TP" or (r[4] is not None and r[4] > 0)]
    losses = [r for r in rows if r[3] == "SL" or (r[4] is not None and r[4] < 0)]

    total_profit = sum(r[4] or 0 for r in rows)

    win_count = len(wins)
    loss_count = len(losses)

    win_rate = round((win_count / total_closed) * 100, 2) if total_closed > 0 else 0

    average_win = round(sum(r[4] for r in wins) / win_count, 2) if win_count > 0 else 0
    average_loss = round(sum(r[4] for r in losses) / loss_count, 2) if loss_count > 0 else 0

    largest_win = round(max([r[4] for r in wins], default=0), 2)
    largest_loss = round(min([r[4] for r in losses], default=0), 2)

    total_wins_money = sum(r[4] for r in wins)
    total_losses_money = abs(sum(r[4] for r in losses))

    profit_factor = round(total_wins_money / total_losses_money, 2) if total_losses_money > 0 else 0

    average_rr = round(sum(r[2] or 0 for r in rows) / total_closed, 2) if total_closed > 0 else 0

    expectancy = round(total_profit / total_closed, 2) if total_closed > 0 else 0

    return {
        "total_closed": total_closed,
        "wins": win_count,
        "losses": loss_count,
        "win_rate": win_rate,
        "total_profit": round(total_profit, 2),
        "average_win": average_win,
        "average_loss": average_loss,
        "largest_win": largest_win,
        "largest_loss": largest_loss,
        "profit_factor": profit_factor,
        "average_rr": average_rr,
        "expectancy": expectancy
    }