import sqlite3
from datetime import datetime

DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def add_column_if_missing(cursor, table, column, column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]

    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def initialise_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades(
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

    add_column_if_missing(cursor, "trades", "followed_plan", "TEXT")
    add_column_if_missing(cursor, "trades", "mistake", "TEXT")
    add_column_if_missing(cursor, "trades", "emotion", "TEXT")
    add_column_if_missing(cursor, "trades", "lesson", "TEXT")
    add_column_if_missing(cursor, "trades", "journal_notes", "TEXT")

    conn.commit()
    conn.close()


def save_trade(trade):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO trades(
        trade_number,
        symbol,
        direction,
        entry,
        stop_loss,
        take_profit,
        risk,
        rr,
        reason,
        telegram_message,
        status
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?)
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM trades")
    count = cursor.fetchone()[0]

    conn.close()

    return f"#{count + 1:03d}"


def get_open_trades():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        trade_number,
        symbol,
        direction,
        entry,
        stop_loss,
        take_profit,
        rr,
        created_at
    FROM trades
    WHERE status='OPEN'
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_trade_by_number(trade_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        trade_number,
        symbol,
        direction,
        entry,
        stop_loss,
        take_profit,
        rr,
        created_at,
        status
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE trades
    SET
        status='CLOSED',
        result=?,
        profit=?,
        closed_at=CURRENT_TIMESTAMP
    WHERE id=?
    """, (
        result,
        profit,
        trade_id
    ))

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


def update_trade_notes(trade_number, followed_plan, mistake, emotion, lesson, journal_notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE trades
    SET
        followed_plan=?,
        mistake=?,
        emotion=?,
        lesson=?,
        journal_notes=?
    WHERE trade_number=?
    """, (
        followed_plan,
        mistake,
        emotion,
        lesson,
        journal_notes,
        trade_number
    ))

    conn.commit()
    conn.close()