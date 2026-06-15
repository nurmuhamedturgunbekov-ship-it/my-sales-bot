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
    waiting_tag = State()
    waiting_payment = State()

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, game TEXT, 
             tag TEXT, price INTEGER, payment TEXT, email TEXT, status TEXT)''')
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
        "🎉 Здесь твои игровые достижения превращаются в реальные деньги. Мы обеспечиваем быстрые выплаты и полную гарантию и защиту для каждой сделки.\n\n"
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
        text = "🧿 Укажите свой тег из Brawl Stars (Пример: `2C9CPP2900`):"
    elif game_key == "cr":
        text = "🖥 Укажите свой тег из Clash Royale (Пример: `VPPLVJ9J8`):"
    else:
        text
