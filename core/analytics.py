import sqlite3
from datetime import datetime, timedelta

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


def calculate_stats_from_rows(rows):
    total_closed = len(rows)

    wins = [r for r in rows if r[3] == "TP" or (r[4] is not None and r[4] > 0)]
    losses = [r for r in rows if r[3] == "SL" or (r[4] is not None and r[4] < 0)]

    total_profit = sum(r[4] or 0 for r in rows)

    win_count = len(wins)
    loss_count = len(losses)

    win_rate = round((win_count / total_closed) * 100, 2) if total_closed > 0 else 0
    average_rr = round(sum(r[2] or 0 for r in rows) / total_closed, 2) if total_closed > 0 else 0
    expectancy = round(total_profit / total_closed, 2) if total_closed > 0 else 0

    return {
        "total_closed": total_closed,
        "wins": win_count,
        "losses": loss_count,
        "win_rate": win_rate,
        "total_profit": round(total_profit, 2),
        "average_rr": average_rr,
        "expectancy": expectancy
    }


def calculate_dashboard_stats():
    rows = fetch_closed_trades()
    stats = calculate_stats_from_rows(rows)

    wins = [r for r in rows if r[4] is not None and r[4] > 0]
    losses = [r for r in rows if r[4] is not None and r[4] < 0]

    stats["average_win"] = round(sum(r[4] for r in wins) / len(wins), 2) if wins else 0
    stats["average_loss"] = round(sum(r[4] for r in losses) / len(losses), 2) if losses else 0
    stats["largest_win"] = round(max([r[4] for r in wins], default=0), 2)
    stats["largest_loss"] = round(min([r[4] for r in losses], default=0), 2)

    total_wins_money = sum(r[4] for r in wins)
    total_losses_money = abs(sum(r[4] for r in losses))

    stats["profit_factor"] = round(total_wins_money / total_losses_money, 2) if total_losses_money > 0 else 0

    return stats


def calculate_recap(period):
    rows = fetch_closed_trades()

    now = datetime.now()

    if period == "week":
        start_date = now - timedelta(days=7)
        title = "Weekly Recap"
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        title = "Monthly Recap"
    else:
        return None

    filtered = []

    for row in rows:
        closed_at = row[6]

        if closed_at is None:
            continue

        try:
            closed_date = datetime.strptime(closed_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue

        if closed_date >= start_date:
            filtered.append(row)

    stats = calculate_stats_from_rows(filtered)
    stats["title"] = title
    stats["period"] = period

    return stats