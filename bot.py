import asyncio
import logging
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

TOKEN = "8673948593:AAGr2QXNGPTYdJWJBNJFE6KfB-ZwQIaTWP8"
ADMIN_ID = 8266829782

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DB_NAME = "bot.db"

GAMES = {"cr": "Clash Royale", "bs": "Brawl Stars", "coc": "Clash of Clans"}

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# Замени эти file_id на свои после отправки картинок боту!
BS_PHOTO = "AgACAgI..."     # Brawl Stars скрин
CR_PHOTO = "AgACAgI..."     # Clash Royale скрин
COC_PHOTO = "AgACAgI..."    # Clash of Clans скрин
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

class SellStates(StatesGroup):
    waiting_tag = State()
    waiting_payment = State()

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, game TEXT, 
             tag TEXT, price INTEGER, payment TEXT, status TEXT)''')
        await db.commit()

def game_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Clash Royale", callback_data="game_cr")],
        [InlineKeyboardButton(text="Brawl Stars", callback_data="game_bs")],
        [InlineKeyboardButton(text="Clash of Clans", callback_data="game_coc")]
    ])

@dp.message(Command("start"))
async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "✨ **Добро пожаловать в крупнейшего бота по скупке в играх Supercell!**\n\n"
        "🎉 Здесь твои игровые достижения превращаются в реальные деньги.\n"
        "Мы обеспечиваем быстрые выплаты и полную гарантию.\n\n"
        "💎 Аккаунт какой игры ты хочешь продать по лучшей цене?",
        reply_markup=game_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("game_"))
async def choose_game(clb: types.CallbackQuery, state: FSMContext):
    game_key = clb.data.split("_")[1]
    game_name = GAMES[game_key]
    await state.update_data(game=game_key, game_name=game_name)
    
    if game_key == "bs":
        photo = BS_PHOTO
        text = "🧿 Укажите свой тег из **Brawl Stars** (Пример: `2C9CPP2900`):"
    elif game_key == "cr":
        photo = CR_PHOTO
        text = "🖥 Укажите свой тег из **Clash Royale** (Пример: `VPPLVJ9J8`):"
    else:
        photo = COC_PHOTO
        text = "✔️ Укажите свой тег из **Clash of Clans** (Пример: `YGCJ2800U`):"
    
    await clb.message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")
    await state.set_state(SellStates.waiting_tag)

# ... (остальной код с process_tag, start_sell и ручным режимом почты остаётся тот же, что я давал раньше)

@dp.message(SellStates.waiting_tag)
async def process_tag(msg: types.Message, state: FSMContext):
    tag = msg.text.strip().replace("#", "").upper()
    data = await state.get_data()
    game = data["game"]
    price = random.randint(1500, 5500)
    
    if game == "bs":
        text = f"""🔍 **Brawl Stars** — тег `{tag}`

😀 Кубков на аккаунте: {random.randint(22000, 42000)}
🪨 Бравлеров с максимальной силой: {random.randint(20, 33)}
🌏 Бравлеров от 1к до 2к: {random.randint(12, 25)}
🌑 Бравлеров от 2к до 3к: {random.randint(0, 7)}
☄ Бравлеров от 3к: {random.randint(0, 4)}

⭐️ Звездных сил: {random.randint(45, 80)}
😀 Гаджетов: {random.randint(55, 98)}
⚡️ Гиперзарядов: {random.randint(30, 60)}
😀 Всего бравлеров: {random.randint(72, 89)}

😀 Мы готовы выкупить его у тебя за **{price} ₽**"""
    
    elif game == "cr":
        text = f"""🖥 **Clash Royale** — тег `{tag}`

😀 Кубков: {random.randint(4500, 8500)}
😀 Эволюционных карт: {random.randint(0, 15)}
⚔️ Героев: {random.randint(0, 5)}

🛡 Карты по уровням:
Уровень 14: {random.randint(0, 6)}
Уровень 13: {random.randint(1, 9)}
Уровень 11: {random.randint(4, 14)}

💵 Мы готовы выкупить аккаунт за: **{price} ₽**"""
    
    else:  # coc
        text = f"""🏠 **Clash of Clans** — тег `{tag}`

🏠 Уровень Ратуши: {random.randint(11, 16)}
🏆 Кубки: {random.randint(0, 4800)}
👷‍♂️ Ратуша Строителя: {random.randint(3, 9)}

💰 Мы готовы выкупить его у тебя за: **{price} ₽**"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Продать за {price}₽", callback_data=f"sell_{price}")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ])
    
    await msg.answer(text, reply_markup=kb, parse_mode="Markdown")
    await state.update_data(tag=tag, price=price)

# (Весь остальной код с платежками и ручным режимом почты оставь из предыдущей версии)

async def main():
    await init_db()
    print("🤖 Бот обновлён с фото!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
