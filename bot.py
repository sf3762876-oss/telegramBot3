# bot.py
# Версия с сохранением данных игроков через SQLite

import asyncio
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8732981892:AAGYHoCOoC7ySdyg-51dnT5Fq8PIt1xHH4I"
ADMIN_ID = 8870697062

bot = Bot(token=TOKEN)
dp = Dispatcher()

db = sqlite3.connect("players.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players(
    tg_id INTEGER PRIMARY KEY,
    nickname TEXT UNIQUE,
    bio TEXT DEFAULT '',
    rank TEXT DEFAULT 'Игрок',
    warns INTEGER DEFAULT 0,
    mute TEXT DEFAULT ''
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bugs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS admins(
    id INTEGER PRIMARY KEY
)
""")

db.commit()

rules_text = "📜 Правила:\n1. Без читов\n2. Без грифа\n3. Уважать игроков"


def is_admin(user_id):
    if user_id == ADMIN_ID:
        return True
    return cur.execute(
        "SELECT id FROM admins WHERE id=?",
        (user_id,)
    ).fetchone() is not None


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Главное меню\n\n"
        "/help - команды\n"
        "/profile - профиль\n"
        "/players - игроки\n"
        "/rules - правила"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "📚 Команды:\n\n"
        "/setnick <ник>\n"
        "/setbio <текст>\n"
        "/profile\n"
        "/rank\n"
        "/players\n"
        "/rules\n"
        "/bug <описание>\n\n"
        "Админ:\n"
        "/setrules <текст>\n"
        "/giverank <ник> <ранг>\n"
        "/warn <ID>\n"
        "/mute <ID>"
    )


@dp.message(Command("setnick"))
async def setnick(message: Message):
    a = message.text.split(maxsplit=1)
    if len(a) < 2:
        return await message.answer("/setnick Ник")

    cur.execute("""
    INSERT INTO players(tg_id,nickname)
    VALUES(?,?)
    ON CONFLICT(tg_id)
    DO UPDATE SET nickname=excluded.nickname
    """, (message.from_user.id, a[1]))

    db.commit()
    await message.answer("✅ Ник сохранён")


@dp.message(Command("setbio"))
async def setbio(message: Message):
    a = message.text.split(maxsplit=1)
    if len(a) < 2:
        return await message.answer("/setbio текст")

    cur.execute(
        "UPDATE players SET bio=? WHERE tg_id=?",
        (a[1], message.from_user.id)
    )
    db.commit()
    await message.answer("✅ Описание сохранено")


@dp.message(Command("profile"))
async def profile(message: Message):
    row = cur.execute(
        "SELECT nickname,bio,rank,warns,mute FROM players WHERE tg_id=?",
        (message.from_user.id,)
    ).fetchone()

    if not row:
        return await message.answer("❌ Сначала установи ник")

    await message.answer(
        f"👤 Профиль\n\n"
        f"Ник: {row[0]}\n"
        f"⭐ Ранг: {row[2]}\n"
        f"⚠️ Варны: {row[3]}\n"
        f"🔇 Мут: {row[4] or 'нет'}\n"
        f"📖 Описание: {row[1]}"
    )


@dp.message(Command("rank"))
async def rank(message: Message):
    row = cur.execute(
        "SELECT rank FROM players WHERE tg_id=?",
        (message.from_user.id,)
    ).fetchone()

    await message.answer(
        f"⭐ Твой ранг: {row[0]}" if row else "Нет профиля"
    )


@dp.message(Command("players"))
async def players(message: Message):
    rows = cur.execute(
        "SELECT nickname,rank FROM players"
    ).fetchall()

    if not rows:
        return await message.answer("Игроков нет")

    await message.answer(
        "\n".join(
            f"{i}. {x[0]} ⭐ {x[1]}"
            for i, x in enumerate(rows, 1)
        )
    )


@dp.message(Command("rules"))
async def rules(message: Message):
    await message.answer(rules_text)


@dp.message(Command("setrules"))
async def setrules(message: Message):
    global rules_text

    if not is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа")

    a = message.text.split(maxsplit=1)

    if len(a) < 2:
        return await message.answer("/setrules текст")

    rules_text = a[1]
    await message.answer("✅ Правила изменены")


@dp.message(Command("giverank"))
async def giverank(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа")

    a = message.text.split()

    if len(a) < 3:
        return await message.answer("/giverank Ник Ранг")

    cur.execute(
        "UPDATE players SET rank=? WHERE nickname=?",
        (a[2], a[1])
    )
    db.commit()

    await message.answer("✅ Ранг изменён")


@dp.message(Command("bug"))
async def bug(message: Message):
    a = message.text.split(maxsplit=1)

    if len(a) < 2:
        return await message.answer("/bug описание")

    cur.execute(
        "INSERT INTO bugs(user_id,text) VALUES(?,?)",
        (message.from_user.id, a[1])
    )
    db.commit()

    await message.answer("🐛 Баг отправлен")


async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
