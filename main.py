import sqlite3
from telegram import 
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = "8288079127:AAG8ij5ugHlVlDQy5MsK3TiooC5rMMrjAEE"

conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    date TEXT,
    category TEXT,
    amount REAL,
    comment TEXT
)
""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт 👋\n"
        "Додай витрату так:\n"
        "/add 250 продукти магазин\n"
        "Подивитись місяць:\n"
        "/month"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        category = context.args[1]
        comment = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO expenses (date, category, amount, comment) VALUES (?, ?, ?, ?)",
            (date, category, amount, comment)
        )
        conn.commit()

        await update.message.reply_text("✅ Витрата додана")
    except:
        await update.message.reply_text("❌ Формат: /add 250 продукти коментар")

async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE date LIKE ?
        GROUP BY category
    """, (datetime.now().strftime("%Y-%m") + "%",))

    rows = cursor.fetchall()
    if not rows:
        await update.message.reply_text("За цей місяць витрат ще немає 🙂")
        return

    text = "📊 Витрати за місяць:\n"
    for cat, total in rows:
        text += f"{cat}: {total:.2f} грн\n"

    await update.message.reply_text(text)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("month", month))
app.run_polling()
