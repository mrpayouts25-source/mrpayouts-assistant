import sqlite3
from datetime import datetime

DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialise_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_number TEXT,
        symbol TEXT,
        direction TEXT,
        entry REAL,
        stop_loss REAL,
        take_profit REAL,
        risk REAL,
        rr REAL,
        reason TEXT,
        telegram_message TEXT,
        status TEXT DEFAULT 'OPEN',
        result TEXT,
        profit REAL,
        closed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_trade(trade):
    initialise_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO trades (
        trade_number, symbol, direction, entry, stop_loss,
        take_profit, risk, rr, reason, telegram_message, status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade["trade_number"],
        trade["symbol"],
        trade["direction"],
        trade["entry"],
        trade["sl"],
        trade["tp"],
        trade["risk"],
        trade["rr"],
        trade["reason"],
        trade["message"],
        "OPEN"
    ))

    conn.commit()
    conn.close()


def get_next_trade_number():
    initialise_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM trades")
    count = cursor.fetchone()[0]

    conn.close()

    return f"#{count + 1:03d}"


def get_open_trades():
    initialise_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, trade_number, symbol, direction, entry,
           stop_loss, take_profit, rr, created_at
    FROM trades
    WHERE status='OPEN'
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_trade_by_number(trade_number):
    initialise_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, trade_number, symbol, direction, entry,
           stop_loss, take_profit, rr, created_at, status
    FROM trades
    WHERE trade_number=?
    """, (trade_number,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "trade_number": row[1],
        "symbol": row[2],
        "direction": row[3],
        "entry": row[4],
        "sl": row[5],
        "tp": row[6],
        "rr": row[7],
        "created_at": row[8],
        "status": row[9]
    }


def close_trade(trade_id, result, profit):
    initialise_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE trades
    SET status='CLOSED',
        result=?,
        profit=?,
        closed_at=CURRENT_TIMESTAMP
    WHERE id=?
    """, (result, profit, trade_id))

    conn.commit()
    conn.close()


def calculate_duration(created_at):
    try:
        opened = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        closed = datetime.now()

        diff = closed - opened

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"

        if hours > 0:
            return f"{hours}h {minutes}m"

        return f"{minutes}m"

    except Exception:
        return "N/A"


def reset_database():
    initialise_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM trades")

    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='trades'")
    except Exception:
        pass

    conn.commit()
    conn.close()