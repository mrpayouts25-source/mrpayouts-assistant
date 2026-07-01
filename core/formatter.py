def format_trade(trade):
    return f"""📊 <b>{trade['trade_number']} | {trade['symbol']} {trade['direction']}</b>

Risk: <code>1%</code>
RR: <code>1:{trade['rr']}</code>

📊 Strategy: <b>HTF Bias • LTF Confirmation</b>

⚠️ Personal trade. Not financial advice."""


def format_result(trade_number, symbol, direction, result, profit, duration="N/A"):
    emoji = "✅" if result == "TP" else "❌" if result == "SL" else "⚪"

    return f"""{emoji} <b>TRADE RESULT</b>

<b>{trade_number} | {symbol} {direction}</b>

Result: <code>{result}</code>
P/L: <code>£{profit}</code>
Duration: <code>{duration}</code>

⚠️ Personal trade. Not financial advice."""


def format_partial(trade_number, symbol, direction, percent):
    return f"""✅ <b>PARTIAL SECURED</b>

<b>{trade_number} | {symbol} {direction}</b>

<code>{percent}%</code> secured.

Remaining position left running.

⚠️ Personal trade. Not financial advice."""


def format_breakeven(trade_number, symbol, direction):
    return f"""🔒 <b>STOP LOSS MOVED TO BREAK EVEN</b>

<b>{trade_number} | {symbol} {direction}</b>

Risk reduced.

⚠️ Personal trade. Not financial advice."""


def format_modify(trade_number, symbol, direction, change_text):
    return f"""🔄 <b>TRADE MODIFIED</b>

<b>{trade_number} | {symbol} {direction}</b>

{change_text}

⚠️ Personal trade. Not financial advice."""


def format_recap(stats):
    return f"""📊 <b>{stats['title']}</b>

Trades Closed: <code>{stats['total_closed']}</code>
Wins: <code>{stats['wins']}</code>
Losses: <code>{stats['losses']}</code>
Win Rate: <code>{stats['win_rate']}%</code>

Net P/L: <code>£{stats['total_profit']}</code>
Average RR: <code>1:{stats['average_rr']}</code>

⚠️ Past performance does not guarantee future results."""