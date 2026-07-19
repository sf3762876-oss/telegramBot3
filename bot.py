import asyncio
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8732981892:AAGYHoCOoC7ySdyg-51dnT5Fq8PIt1xHH4I"

bot = Bot(token=TOKEN)
dp = Dispatcher()

db = sqlite3.connect("players.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players(
    tg_id INTEGER PRIMARY KEY,
    nickname TEXT UNIQUE,
    bio TEXT DEFAULT '',
    rank TEXT DEFAULT 'Игрок'
)
""")
db.commit()

rules_text = """📜 Правила сервера:

1. Не использовать читы.
2. Не гриферить.
3. Не оскорблять игроков.
4. Не использовать баги.
5. Уважать администрацию.
"""

ADMIN_ID = 8870697062  # замени на свой Telegram ID

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "📚 Команды:\n"
        "/help - список команд\n"
        "/rules - правила\n"
        "/players - игроки\n"
        "/setnick <ник>\n"
        "/setbio <описание>\n"
        "/nimi <ник>\n"
        "/rank - твой ранг"
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "📚 Команды бота:\n\n"
        "/start - меню\n"
        "/help - помощь\n"
        "/rules - правила сервера\n"
        "/players - список игроков\n"
        "/setnick <ник> - установить ник\n"
        "/setbio <описание> - описание\n"
        "/nimi <ник> - профиль игрока\n"
        "/rank - свой ранг\n"
        "/setrules - изменить правила (админ)"
    )

@dp.message(Command("rules"))
async def rules(message: Message):
    await message.answer(rules_text)

@dp.message(Command("players"))
async def players(message: Message):
    cur.execute("SELECT nickname, rank FROM players ORDER BY nickname")
    rows = cur.fetchall()

    if not rows:
        await message.answer("❌ Игроков пока нет.")
        return

    text = "👥 Игроки сервера:\n\n"
    for i, row in enumerate(rows, 1):
        text += f"{i}. {row[0]} ⭐ {row[1]}\n"

    await message.answer(text)

@dp.message(Command("setnick"))
async def setnick(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/setnick ВашНик")
        return

    nick = args[1]

    cur.execute("SELECT bio FROM players WHERE tg_id=?", (message.from_user.id,))
    row = cur.fetchone()
    bio = row[0] if row else ""

    cur.execute("""
    INSERT INTO players(tg_id, nickname, bio, rank)
    VALUES(?,?,?,?)
    ON CONFLICT(tg_id)
    DO UPDATE SET nickname=excluded.nickname
    """, (message.from_user.id, nick, bio, "Игрок"))

    db.commit()
    await message.answer(f"✅ Ник сохранён: {nick}")

@dp.message(Command("setbio"))
async def setbio(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/setbio описание")
        return

    cur.execute(
        "UPDATE players SET bio=? WHERE tg_id=?",
        (args[1], message.from_user.id)
    )
    db.commit()

    await message.answer("✅ Описание сохранено")

@dp.message(Command("nimi"))
async def nimi(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/nimi Ник")
        return

    cur.execute(
        "SELECT bio, rank FROM players WHERE nickname=?",
        (args[1],)
    )
    row = cur.fetchone()

    if row:
        await message.answer(
            f"📜 Игрок: {args[1]}\n"
            f"⭐ Ранг: {row[1]}\n\n"
            f"{row[0]}"
        )
    else:
        await message.answer("❌ Игрок не найден")

@dp.message(Command("rank"))
async def rank(message: Message):
    cur.execute(
        "SELECT nickname, rank FROM players WHERE tg_id=?",
        (message.from_user.id,)
    )
    row = cur.fetchone()

    if row:
        await message.answer(f"⭐ {row[0]}\nТвой ранг: {row[1]}")
    else:
        await message.answer("Сначала установи ник")

@dp.message(Command("setrules"))
async def setrules(message: Message):


global rules_text

    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет доступа")
        return

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/setrules новые правила")
        return

    rules_text = args[1]
    await message.answer("✅ Правила обновлены")

async def main():
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
