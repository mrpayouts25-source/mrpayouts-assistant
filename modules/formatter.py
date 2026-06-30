def format_trade_signal(trade_number, symbol, direction, entry, sl, tp, risk, reason):
    return f"""
━━━━━━━━━━━━━━━━━━
📈 *TRADE {trade_number}*

*{symbol} • {direction}*

📍 Entry
`{entry}`

🛑 Stop Loss
`{sl}`

🎯 Take Profit
`{tp}`

⚖️ Risk
`{risk}%`

🧠 Reason
{reason}

━━━━━━━━━━━━━━━━━━
⚠️ Personal trade. Not financial advice.
━━━━━━━━━━━━━━━━━━
"""