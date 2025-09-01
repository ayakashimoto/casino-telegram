#!/usr/bin/env python3
"""
Утилита для управления казино-ботом
"""

import sys
import subprocess
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def check_requirements():
    """Проверка зависимостей"""
    try:
        import aiogram
        from dotenv import load_dotenv
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def check_config():
    """Проверка конфигурации"""
    bot_token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")

    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Не настроен BOT_TOKEN в .env файле")
        print("Получите токен у @BotFather в Telegram")
        return False

    if not admin_id or admin_id == "123456789":
        print("❌ Не настроен ADMIN_ID в .env файле")
        print("Укажите ваш Telegram ID")
        return False

    print("✅ Конфигурация корректна")
    return True

def init_database():
    """Инициализация базы данных"""
    from bot import Database
    db = Database()
    print("✅ База данных инициализирована")

    # Создаем базовые промокоды
    db.create_promo("WELCOME", 1000, 100)
    db.create_promo("LUCKY", 500, 50)
    db.create_promo("BONUS777", 777, 25)
    print("✅ Базовые промокоды созданы")

def show_stats():
    """Показать статистику"""
    if not os.path.exists('casino.db'):
        print("❌ База данных не найдена. Запустите бота сначала.")
        return

    conn = sqlite3.connect('casino.db')
    c = conn.cursor()

    users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    games = c.execute('SELECT COUNT(*) FROM games').fetchone()[0]
    total_bets = c.execute('SELECT SUM(bet) FROM games').fetchone()[0] or 0
    total_wins = c.execute('SELECT SUM(result) FROM games').fetchone()[0] or 0

    print(f"""
📊 Статистика бота:
👥 Пользователей: {users}
🎮 Игр сыграно: {games}
💸 Общие ставки: {total_bets}
🏆 Общие выплаты: {total_wins}
💰 Прибыль казино: {total_bets - total_wins}
""")

    # Топ игроки
    top = c.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5').fetchall()
    print("🏆 Топ игроков:")
    for i, (name, balance) in enumerate(top, 1):
        print(f"{i}. {name or 'Аноним'}: {balance} очков")

    conn.close()

def backup_database():
    """Создать резервную копию БД"""
    if not os.path.exists('casino.db'):
        print("❌ База данных не найдена")
        return

    from datetime import datetime
    backup_name = f"casino_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    import shutil
    shutil.copy2('casino.db', backup_name)
    print(f"✅ Резервная копия создана: {backup_name}")

def run_bot():
    """Запуск бота"""
    if not check_requirements():
        return

    if not check_config():
        return

    print("🎰 Запуск казино-бота...")
    try:
        subprocess.run([sys.executable, "bot.py"])
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")

def main():
    if len(sys.argv) < 2:
        print("""
🎰 Управление казино-ботом

Команды:
  run      - Запустить бота
  check    - Проверить настройки
  init     - Инициализировать БД
  stats    - Показать статистику
  backup   - Создать резервную копию БД

Примеры:
  python run.py run
  python run.py stats
""")
        return

    command = sys.argv[1]

    if command == "run":
        run_bot()
    elif command == "check":
        check_requirements()
        check_config()
    elif command == "init":
        init_database()
    elif command == "stats":
        show_stats()
    elif command == "backup":
        backup_database()
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main()
