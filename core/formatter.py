def format_trade(trade):
    return f"""📊 <b>{trade['trade_number']}</b> | <b>{trade['symbol']} {trade['direction']}</b>

Entry: <code>{trade['entry']}</code>
SL: <code>{trade['sl']}</code>
TP: <code>{trade['tp']}</code>
Risk: <code>{trade['risk']}%</code>
RR: <code>1:{trade['rr']}</code>

🧠 {trade['reason']}

⚠️ Personal trade. Not financial advice."""
    

def format_result(trade_number, symbol, direction, result, profit):
    emoji = "✅" if result == "TP" else "❌" if result == "SL" else "⚪"

    return f"""{emoji} <b>TRADE RESULT</b>

<b>{trade_number}</b> | <b>{symbol} {direction}</b>

Result: <code>{result}</code>
P/L: <code>£{profit}</code>

⚠️ Personal trade. Not financial advice."""