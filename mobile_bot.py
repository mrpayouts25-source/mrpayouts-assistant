from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
import os

from core.parser import parse_ctrader_link
from core.calculator import calculate_rr
from core.formatter import (
    format_trade,
    format_result,
    format_partial,
    format_breakeven,
    format_modify,
    format_recap
)
from core.database import (
    initialise_database,
    save_trade,
    get_next_trade_number,
    get_trade_by_number,
    get_open_trades,
    close_trade,
    calculate_duration,
    reset_database
)
from core.image_generator import (
    generate_trade_image,
    generate_result_image,
    generate_update_image
)
from core.telegram import send_photo, send_message
from core.analytics import calculate_recap

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

SIGNAL_LINK, SIGNAL_ENTRY = range(2)
CLOSE_TRADE_NUMBER, CLOSE_PROFIT = range(2, 4)
PARTIAL_TRADE_NUMBER, PARTIAL_PERCENT = range(4, 6)
BE_TRADE_NUMBER = 6
MODIFY_TRADE_NUMBER, MODIFY_TEXT = range(7, 9)


def authorised(update: Update):
    return update.effective_user.id == ALLOWED_USER_ID


def normalise_trade_number(raw):
    return "#" + raw.replace("#", "").zfill(3)


async def help_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return

    await update.message.reply_text(
        "MrPayouts Mobile Bot\n\n"
        "/signal - create signal\n"
        "/modify - modify SL or TP\n"
        "/be - move SL to breakeven\n"
        "/partial - partial secured\n"
        "/tp - close as TP\n"
        "/sl - close as SL\n"
        "/manual - manual close\n"
        "/open - show open trades\n"
        "/stats - show basic stats\n"
        "/recap week - post weekly recap\n"
        "/recap month - post monthly recap\n"
        "/cancel - cancel current action"
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    await update.message.reply_text("Paste the cTrader share link:")
    return SIGNAL_LINK


async def receive_signal_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    context.user_data["link"] = update.message.text.strip()
    await update.message.reply_text("Entry price?")
    return SIGNAL_ENTRY


async def receive_signal_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    try:
        parsed = parse_ctrader_link(context.user_data["link"])
        entry = float(update.message.text.strip())

        trade = {
            "trade_number": get_next_trade_number(),
            "symbol": parsed["symbol"],
            "direction": parsed["direction"],
            "entry": entry,
            "sl": parsed["sl"],
            "tp": parsed["tp"],
            "risk": 1,
            "reason": "HTF Bias • LTF Confirmation"
        }

        trade["rr"] = calculate_rr(trade["entry"], trade["sl"], trade["tp"])
        trade["message"] = format_trade(trade)

        image_path = generate_trade_image(trade)
        sent = send_photo(image_path, caption=trade["message"])

        if sent:
            save_trade(trade)
            await update.message.reply_text("✅ Signal posted and saved.")
        else:
            await update.message.reply_text("❌ Telegram post failed.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    return ConversationHandler.END


async def close_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    context.user_data["close_result"] = update.message.text.replace("/", "").strip().upper()
    await update.message.reply_text("Trade number?")
    return CLOSE_TRADE_NUMBER


async def receive_close_trade_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    context.user_data["close_trade_number"] = normalise_trade_number(update.message.text.strip())
    await update.message.reply_text("Profit / loss amount? Example: 285 or -100")
    return CLOSE_PROFIT


async def receive_close_profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    try:
        trade_number = context.user_data["close_trade_number"]
        result = context.user_data["close_result"]
        profit = float(update.message.text.strip())

        trade = get_trade_by_number(trade_number)

        if trade is None:
            await update.message.reply_text("Trade not found.")
            return ConversationHandler.END

        if trade["status"] != "OPEN":
            await update.message.reply_text("Trade is already closed.")
            return ConversationHandler.END

        duration = calculate_duration(trade["created_at"])
        close_trade(trade["id"], result, profit)

        result_message = format_result(
            trade["trade_number"],
            trade["symbol"],
            trade["direction"],
            result,
            profit,
            duration
        )

        image_path = generate_result_image(trade, result, profit)
        sent = send_photo(image_path, caption=result_message)

        if sent:
            await update.message.reply_text(f"✅ Trade {trade_number} closed as {result}.\nDuration: {duration}")
        else:
            await update.message.reply_text("Trade closed, but result post failed.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    return ConversationHandler.END


async def partial_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    await update.message.reply_text("Trade number?")
    return PARTIAL_TRADE_NUMBER


async def receive_partial_trade_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    context.user_data["partial_trade_number"] = normalise_trade_number(update.message.text.strip())
    await update.message.reply_text("What % secured?")
    return PARTIAL_PERCENT


async def receive_partial_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    try:
        trade_number = context.user_data["partial_trade_number"]
        percent = update.message.text.strip()

        trade = get_trade_by_number(trade_number)

        if trade is None:
            await update.message.reply_text("Trade not found.")
            return ConversationHandler.END

        message = format_partial(trade["trade_number"], trade["symbol"], trade["direction"], percent)
        image_path = generate_update_image(trade, "Partial Secured", f"{percent}% secured. Runner left open.")

        sent = send_photo(image_path, caption=message)

        if sent:
            await update.message.reply_text(f"✅ Partial update posted for {trade_number}.")
        else:
            await update.message.reply_text("❌ Partial update failed.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    return ConversationHandler.END


async def be_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    await update.message.reply_text("Trade number?")
    return BE_TRADE_NUMBER


async def receive_be_trade_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    try:
        trade_number = normalise_trade_number(update.message.text.strip())
        trade = get_trade_by_number(trade_number)

        if trade is None:
            await update.message.reply_text("Trade not found.")
            return ConversationHandler.END

        message = format_breakeven(trade["trade_number"], trade["symbol"], trade["direction"])
        image_path = generate_update_image(trade, "Break Even", "Stop loss moved to break even.")

        sent = send_photo(image_path, caption=message)

        if sent:
            await update.message.reply_text(f"✅ Breakeven update posted for {trade_number}.")
        else:
            await update.message.reply_text("❌ Breakeven update failed.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    return ConversationHandler.END


async def modify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    await update.message.reply_text("Trade number?")
    return MODIFY_TRADE_NUMBER


async def receive_modify_trade_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    context.user_data["modify_trade_number"] = normalise_trade_number(update.message.text.strip())
    await update.message.reply_text("What changed? Example: SL moved to 4050 or TP moved to 3920")
    return MODIFY_TEXT


async def receive_modify_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    try:
        trade_number = context.user_data["modify_trade_number"]
        change_text = update.message.text.strip()

        trade = get_trade_by_number(trade_number)

        if trade is None:
            await update.message.reply_text("Trade not found.")
            return ConversationHandler.END

        message = format_modify(trade["trade_number"], trade["symbol"], trade["direction"], change_text)
        image_path = generate_update_image(trade, "Trade Modified", change_text)

        sent = send_photo(image_path, caption=message)

        if sent:
            await update.message.reply_text(f"✅ Modify update posted for {trade_number}.")
        else:
            await update.message.reply_text("❌ Modify update failed.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    return ConversationHandler.END


async def open_trades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return

    rows = get_open_trades()

    if not rows:
        await update.message.reply_text("No open trades.")
        return

    text = "Open Trades\n\n"

    for row in rows:
        text += f"{row[1]} | {row[2]} {row[3]} | RR 1:{row[7]}\n"

    await update.message.reply_text(text)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return

    from core.analytics import calculate_dashboard_stats

    s = calculate_dashboard_stats()

    await update.message.reply_text(
        f"Stats\n\n"
        f"Closed Trades: {s['total_closed']}\n"
        f"Wins: {s['wins']}\n"
        f"Losses: {s['losses']}\n"
        f"Win Rate: {s['win_rate']}%\n"
        f"Total P/L: £{s['total_profit']}\n"
        f"Average RR: 1:{s['average_rr']}\n"
        f"Expectancy: £{s['expectancy']}"
    )


async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return

    try:
        if len(context.args) != 1 or context.args[0].lower() not in ["week", "month"]:
            await update.message.reply_text("Usage:\n/recap week\n/recap month")
            return

        recap_stats = calculate_recap(context.args[0].lower())
        message = format_recap(recap_stats)
        sent = send_message(message)

        if sent:
            await update.message.reply_text(f"✅ {recap_stats['title']} posted.")
        else:
            await update.message.reply_text("❌ Recap failed.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def resetdb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return

    reset_database()

    await update.message.reply_text(
        "✅ Database reset successfully.\n\n"
        "• All trades deleted\n"
        "• Statistics reset\n"
        "• Next trade will be #001"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorised(update):
        return ConversationHandler.END

    context.user_data.clear()
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


async def set_commands(app):
    commands = [
        BotCommand("start", "Show commands"),
        BotCommand("help", "Show commands"),
        BotCommand("signal", "Create signal"),
        BotCommand("modify", "Modify SL or TP"),
        BotCommand("be", "Move SL to breakeven"),
        BotCommand("partial", "Partial secured"),
        BotCommand("tp", "Close as TP"),
        BotCommand("sl", "Close as SL"),
        BotCommand("manual", "Manual close"),
        BotCommand("open", "Show open trades"),
        BotCommand("stats", "Show stats"),
        BotCommand("recap", "Post weekly/monthly recap"),
        BotCommand("cancel", "Cancel current action"),
    ]

    await app.bot.set_my_commands(commands)


def main():
    initialise_database()

    app = Application.builder().token(BOT_TOKEN).post_init(set_commands).build()

    signal_conversation = ConversationHandler(
        entry_points=[CommandHandler("signal", signal)],
        states={
            SIGNAL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_signal_link)],
            SIGNAL_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_signal_entry)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    close_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("tp", close_start),
            CommandHandler("sl", close_start),
            CommandHandler("manual", close_start),
        ],
        states={
            CLOSE_TRADE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_close_trade_number)],
            CLOSE_PROFIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_close_profit)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    partial_conversation = ConversationHandler(
        entry_points=[CommandHandler("partial", partial_start)],
        states={
            PARTIAL_TRADE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_partial_trade_number)],
            PARTIAL_PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_partial_percent)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    be_conversation = ConversationHandler(
        entry_points=[CommandHandler("be", be_start)],
        states={
            BE_TRADE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_be_trade_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    modify_conversation = ConversationHandler(
        entry_points=[CommandHandler("modify", modify_start)],
        states={
            MODIFY_TRADE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_modify_trade_number)],
            MODIFY_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_modify_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", help_text))
    app.add_handler(CommandHandler("help", help_text))
    app.add_handler(signal_conversation)
    app.add_handler(modify_conversation)
    app.add_handler(be_conversation)
    app.add_handler(partial_conversation)
    app.add_handler(close_conversation)
    app.add_handler(CommandHandler("open", open_trades))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("recap", recap))
    app.add_handler(CommandHandler("resetdb", resetdb))

    app.run_polling()


if __name__ == "__main__":
    main()
