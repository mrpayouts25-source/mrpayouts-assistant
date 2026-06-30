def format_trade(trade):
    return f"""📊 TRADE {trade['trade_number']}

{trade['symbol']} • {trade['direction']}

━━━━━━━━━━━━━━━━━━

📍 Entry
{trade['entry']}

🛑 Stop Loss
{trade['sl']}

🎯 Take Profit
{trade['tp']}

⚖️ Risk
{trade['risk']}%

📈 RR
1:{trade['rr']}

🧠 Reason

{trade['reason']}

━━━━━━━━━━━━━━━━━━

⚠️ Personal trade.
Not financial advice.
"""


def format_result(trade_number, symbol, direction, result, profit):
    emoji = "✅" if result == "TP" else "❌" if result == "SL" else "⚪"

    return f"""{emoji} TRADE RESULT

{trade_number}

{symbol} • {direction}

Result
{result}

P/L
£{profit}

━━━━━━━━━━━━━━━━━━

⚠️ Personal trade.
Not financial advice.
"""