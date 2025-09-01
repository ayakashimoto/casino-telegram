import asyncio
import sqlite3
import logging
import secrets
from datetime import datetime
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(storage=MemoryStorage())

class GameStates(StatesGroup):
    waiting_bet = State()
    waiting_choice = State()
    promo_input = State()

# База данных
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('casino.db', check_same_thread=False)
        self.init()

    def init(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 1000,
            last_bonus DATE, total_games INTEGER DEFAULT 0, total_wins INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, game_type TEXT,
            bet INTEGER, result INTEGER, multiplier REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY, reward INTEGER, max_uses INTEGER,
            current_uses INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS used_promos (
            user_id INTEGER, promo_code TEXT, PRIMARY KEY (user_id, promo_code))''')
        self.conn.commit()

    def get_user(self, user_id):
        return self.conn.cursor().execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()

    def create_user(self, user_id, username=None):
        self.conn.cursor().execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        self.conn.commit()

    def get_balance(self, user_id):
        user = self.get_user(user_id)
        return user[2] if user else 0

    def update_balance(self, user_id, amount):
        self.conn.cursor().execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        self.conn.commit()

    def can_bonus(self, user_id):
        user = self.get_user(user_id)
        if not user or not user[3]: return True
        return datetime.now().date() > datetime.strptime(user[3], '%Y-%m-%d').date()

    def claim_bonus(self, user_id):
        c = self.conn.cursor()
        c.execute('UPDATE users SET balance = balance + 500, last_bonus = ? WHERE user_id = ?',
                 (datetime.now().date().isoformat(), user_id))
        self.conn.commit()

    def add_game(self, user_id, game_type, bet, result, multiplier):
        c = self.conn.cursor()
        c.execute('INSERT INTO games VALUES (NULL, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
                 (user_id, game_type, bet, result, multiplier))
        won = 1 if result > 0 else 0
        c.execute('UPDATE users SET total_games = total_games + 1, total_wins = total_wins + ? WHERE user_id = ?',
                 (won, user_id))
        self.conn.commit()

    def get_top(self, limit=10):
        return self.conn.cursor().execute('''SELECT username, balance, total_games, total_wins
                                           FROM users ORDER BY balance DESC LIMIT ?''', (limit,)).fetchall()

    def create_promo(self, code, reward, max_uses=1):
        self.conn.cursor().execute('INSERT OR REPLACE INTO promo_codes VALUES (?, ?, ?, 0)',
                                  (code, reward, max_uses))
        self.conn.commit()

    def use_promo(self, user_id, code):
        c = self.conn.cursor()
        promo = c.execute('SELECT * FROM promo_codes WHERE code = ?', (code,)).fetchone()
        if not promo: return False, "Промокод не найден"

        used = c.execute('SELECT * FROM used_promos WHERE user_id = ? AND promo_code = ?',
                        (user_id, code)).fetchone()
        if used: return False, "Уже использован"

        if promo[3] >= promo[2]: return False, "Промокод исчерпан"

        c.execute('INSERT INTO used_promos VALUES (?, ?)', (user_id, code))
        c.execute('UPDATE promo_codes SET current_uses = current_uses + 1 WHERE code = ?', (code,))
        c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (promo[1], user_id))
        self.conn.commit()
        return True, f"Получено {promo[1]} очков"

db = DB()

# Клавиатуры
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Игры", callback_data="games")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
         InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton(text="🏆 Рейтинг", callback_data="rating"),
         InlineKeyboardButton(text="🏷 Промокод", callback_data="promo")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])

def games_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Монетка", callback_data="game_coinflip"),
         InlineKeyboardButton(text="🎲 Кости", callback_data="game_dice")],
        [InlineKeyboardButton(text="🎰 Слоты", callback_data="game_slots"),
         InlineKeyboardButton(text="🎯 Рулетка", callback_data="game_roulette")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main")]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main")]
    ])

# Игры
def coinflip(choice):
    result = secrets.choice(['heads', 'tails'])
    won = choice == result
    msg = f"🪙 Выпал {'орёл' if result == 'heads' else 'решка'}!"
    return won, msg, 2.0 if won else 0.0

def dice():
    result = secrets.randbelow(6) + 1
    msg = f"🎲 Выпало: {result}"
    if result == 6: return True, msg + " 🎉", 5.0
    elif result in [4, 5]: return True, msg + " ✨", 2.0
    else: return False, msg + " 😔", 0.0

def slots():
    symbols = ['🍎', '🍊', '🍇', '🍋', '🍒', '⭐']
    result = [secrets.choice(symbols) for _ in range(3)]
    msg = f"🎰 {''.join(result)}"
    if result[0] == result[1] == result[2]: return True, msg + "\n🎉 ТРИ!", 10.0
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        return True, msg + "\n✨ Пара!", 3.0
    else: return False, msg + "\n😔", 0.0

def roulette(bet_type, bet_value=None):
    number = secrets.randbelow(37)
    color = 'green' if number == 0 else ('red' if number % 2 == 1 else 'black')
    msg = f"🎯 {number} ({'🟢' if color == 'green' else '🔴' if color == 'red' else '⚫'})"

    if bet_type == 'number' and bet_value and int(bet_value) == number:
        return True, msg + "\n🎉 ТОЧНО!", 36.0
    elif bet_type == 'color' and bet_value == color and color != 'green':
        return True, msg + "\n✨ Цвет!", 2.0
    elif bet_type == 'even' and number != 0 and number % 2 == 0:
        return True, msg + "\n✨ Чёт!", 2.0
    elif bet_type == 'odd' and number != 0 and number % 2 == 1:
        return True, msg + "\n✨ Нечёт!", 2.0
    return False, msg + "\n😔", 0.0

# Обработчики
@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    db.create_user(user_id, username)
    balance = db.get_balance(user_id)

    text = f"""🎰 *Казино\\-Бот* 🎰

💰 Баланс: *{balance}* очков
🎮 7 захватывающих игр
🎁 Ежедневные бонусы\\!"""

    await message.answer(text, reply_markup=main_kb())

@dp.callback_query(F.data == "main")
async def main_menu(callback: types.CallbackQuery):
    balance = db.get_balance(callback.from_user.id)
    text = f"🎰 *Главное меню*\n💰 Баланс: *{balance}* очков"
    await callback.message.edit_text(text, reply_markup=main_kb())

@dp.callback_query(F.data == "games")
async def games_menu(callback: types.CallbackQuery):
    text = """🎮 *Игры:*

🪙 *Монетка* \\- ×2
🎲 *Кости* \\- ×2 или ×5
🎰 *Слоты* \\- ×3 или ×10
🎯 *Рулетка* \\- ×2 или ×36"""
    await callback.message.edit_text(text, reply_markup=games_kb())

@dp.callback_query(F.data == "profile")
async def profile(callback: types.CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if user:
        rate = (user[5] / user[4] * 100) if user[4] > 0 else 0
        text = f"""👤 *Профиль*

🆔 @{user[1] or 'Аноним'}
💰 {user[2]} очков
🎮 Игр: {user[4]}
🏆 Побед: {user[5]}
📊 Винрейт: {rate:.1f}%"""
    else: text = "Ошибка"
    await callback.message.edit_text(text, reply_markup=back_kb())

@dp.callback_query(F.data == "bonus")
async def bonus(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if db.can_bonus(user_id):
        db.claim_bonus(user_id)
        text = "🎁 *Бонус получен\\!*\n💰 \\+500 очков"
    else:
        text = "🎁 *Бонус*\n❌ Уже получен сегодня"
    await callback.message.edit_text(text, reply_markup=back_kb())

@dp.callback_query(F.data == "rating")
async def rating(callback: types.CallbackQuery):
    top = db.get_top(10)
    text = "🏆 *ТОП\\-10*\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, player in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}\\."
        username = player[0] or "Аноним"
        rate = (player[3] / player[2] * 100) if player[2] > 0 else 0
        text += f"{medal} *{username}* \\- {player[1]} \\({rate:.0f}%\\)\n"

    await callback.message.edit_text(text, reply_markup=back_kb())

@dp.callback_query(F.data == "promo")
async def promo(callback: types.CallbackQuery, state: FSMContext):
    text = "🏷 *Введите промокод:*"
    await callback.message.edit_text(text, reply_markup=back_kb())
    await state.set_state(GameStates.promo_input)

@dp.callback_query(F.data == "help")
async def help_menu(callback: types.CallbackQuery):
    text = """ℹ️ *Помощь*

💰 Старт: 1000 очков
🎁 Бонус: 500 очков/день
🎮 Мин\\. ставка: 100 очков

🎯 *Выплаты:*
• Монетка: ×2
• Кости: ×2/×5
• Слоты: ×3/×10
• Рулетка: ×2/×36"""
    await callback.message.edit_text(text, reply_markup=back_kb())

@dp.callback_query(F.data.startswith("game_"))
async def game_start(callback: types.CallbackQuery, state: FSMContext):
    game = callback.data.split("_")[1]
    await state.update_data(game=game)
    text = f"🎮 *{game.upper()}*\n💰 Введите ставку \\(мин\\. 100\\):"
    await callback.message.edit_text(text, reply_markup=back_kb())
    await state.set_state(GameStates.waiting_bet)

@dp.message(GameStates.waiting_bet)
async def handle_bet(message: Message, state: FSMContext):
    try:
        bet = int(message.text)
        user_id = message.from_user.id
        balance = db.get_balance(user_id)

        if bet < 100:
            await message.answer("❌ Минимум 100 очков!")
            return
        if bet > balance:
            await message.answer("❌ Недостаточно средств!")
            return

        data = await state.get_data()
        game = data['game']
        db.update_balance(user_id, -bet)

        if game == "coinflip":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🪙 Орёл", callback_data="choice_heads"),
                 InlineKeyboardButton(text="🪙 Решка", callback_data="choice_tails")]
            ])
            await message.answer("🪙 Выберите:", reply_markup=kb)
            await state.update_data(bet=bet)
            await state.set_state(GameStates.waiting_choice)
            return

        elif game == "dice":
            won, msg, mult = dice()
        elif game == "slots":
            anim = await message.answer("🎰 🎲 🎲")
            await asyncio.sleep(0.5)
            await anim.edit_text("🎰 🎰 🎲")
            await asyncio.sleep(0.5)
            await anim.edit_text("🎰 🎰 🎰")
            await asyncio.sleep(0.5)
            won, msg, mult = slots()
            await anim.delete()
        elif game == "roulette":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔴 Красное", callback_data="roul_color_red"),
                 InlineKeyboardButton(text="⚫ Чёрное", callback_data="roul_color_black")],
                [InlineKeyboardButton(text="📈 Чёт", callback_data="roul_even"),
                 InlineKeyboardButton(text="📉 Нечёт", callback_data="roul_odd")]
            ])
            await message.answer("🎯 Выберите:", reply_markup=kb)
            await state.update_data(bet=bet)
            await state.set_state(GameStates.waiting_choice)
            return

        result = int(bet * mult) if won else 0
        if won: db.update_balance(user_id, result)
        db.add_game(user_id, game, bet, result, mult)

        final = f"{msg}\n\n"
        final += f"🎉 Выигрыш: {result} очков!" if won else "😔 Проигрыш!"
        await message.answer(final, reply_markup=back_kb())
        await state.clear()

    except ValueError:
        await message.answer("❌ Введите число!")

@dp.callback_query(F.data.startswith("choice_"))
async def handle_choice(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[1]
    data = await state.get_data()
    bet, game = data['bet'], data['game']
    user_id = callback.from_user.id

    won, msg, mult = coinflip(choice)
    result = int(bet * mult) if won else 0
    if won: db.update_balance(user_id, result)
    db.add_game(user_id, game, bet, result, mult)

    final = f"{msg}\n\n"
    final += f"🎉 Выигрыш: {result} очков!" if won else "😔 Проигрыш!"
    await callback.message.edit_text(final, reply_markup=back_kb())
    await state.clear()

@dp.callback_query(F.data.startswith("roul_"))
async def handle_roulette(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")[1:]
    data = await state.get_data()
    bet = data['bet']
    user_id = callback.from_user.id

    bet_type = parts[0]
    bet_value = parts[1] if len(parts) > 1 else None

    won, msg, mult = roulette(bet_type, bet_value)
    result = int(bet * mult) if won else 0
    if won: db.update_balance(user_id, result)
    db.add_game(user_id, "roulette", bet, result, mult)

    final = f"{msg}\n\n"
    final += f"🎉 Выигрыш: {result} очков!" if won else "😔 Проигрыш!"
    await callback.message.edit_text(final, reply_markup=back_kb())
    await state.clear()

@dp.message(GameStates.promo_input)
async def handle_promo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip().upper()
    success, msg = db.use_promo(user_id, code)
    text = f"{'✅' if success else '❌'} {msg}"
    await message.answer(text, reply_markup=back_kb())
    await state.clear()

# Админ команды
@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("👑 *Админ*\n\n/createpromo CODE REWARD\n/stats")

@dp.message(Command("createpromo"))
async def create_promo(message: Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        code, reward = parts[1].upper(), int(parts[2])
        db.create_promo(code, reward, 999)
        await message.answer(f"✅ Промокод {code} создан!")
    except: await message.answer("❌ Формат: /createpromo CODE REWARD")

@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id != ADMIN_ID: return
    c = db.conn.cursor()
    users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    games = c.execute('SELECT COUNT(*) FROM games').fetchone()[0]
    bets = c.execute('SELECT SUM(bet) FROM games').fetchone()[0] or 0
    wins = c.execute('SELECT SUM(result) FROM games').fetchone()[0] or 0

    text = f"""📊 *Статистика*

👥 Пользователей: {users}
🎮 Игр: {games}
💸 Ставок: {bets}
🏆 Выплат: {wins}
💰 Прибыль: {bets - wins}"""
    await message.answer(text)

async def main():
    try:
        print("🎰 Казино-бот запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
