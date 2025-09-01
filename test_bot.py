#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функций казино-бота
Запуск: python test_bot.py
"""

import sqlite3
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Тест базы данных"""
    print("🧪 Тестирование базы данных...")

    try:
        from bot import Database
        db = Database()

        # Тест создания пользователя
        test_user_id = 999999999
        db.create_user(test_user_id, "test_user")
        user = db.get_user(test_user_id)

        if user and user[2] == 1000:  # Стартовый баланс
            print("✅ Создание пользователя работает")
        else:
            print("❌ Ошибка создания пользователя")
            return False

        # Тест обновления баланса
        db.update_balance(test_user_id, 500)
        balance = db.get_balance(test_user_id)

        if balance == 1500:
            print("✅ Обновление баланса работает")
        else:
            print("❌ Ошибка обновления баланса")
            return False

        # Тест промокода
        db.create_promo("TEST123", 777, 1)
        success, msg = db.use_promo(test_user_id, "TEST123")

        if success:
            print("✅ Система промокодов работает")
        else:
            print("❌ Ошибка промокодов")
            return False

        # Очистка тестовых данных
        cursor = db.conn.cursor()
        cursor.execute('DELETE FROM users WHERE user_id = ?', (test_user_id,))
        cursor.execute('DELETE FROM promo_codes WHERE code = ?', ("TEST123",))
        cursor.execute('DELETE FROM used_promos WHERE user_id = ?', (test_user_id,))
        db.conn.commit()

        print("✅ База данных протестирована успешно")
        return True

    except Exception as e:
        print(f"❌ Ошибка тестирования БД: {e}")
        return False

def test_games():
    """Тест игровых функций"""
    print("\n🎮 Тестирование игр...")

    try:
        # Импортируем игровые функции из bot.py
        from bot import coinflip, dice, slots, roulette

        # Тест монетки
        won, msg, mult = coinflip('heads')
        if isinstance(won, bool) and isinstance(mult, float):
            print("✅ Монетка работает")
        else:
            print("❌ Ошибка в монетке")
            return False

        # Тест костей
        won, msg, mult = dice()
        if isinstance(won, bool) and mult in [0.0, 2.0, 5.0]:
            print("✅ Кости работают")
        else:
            print("❌ Ошибка в костях")
            return False

        # Тест слотов
        won, msg, mult = slots()
        if isinstance(won, bool) and mult in [0.0, 3.0, 10.0]:
            print("✅ Слоты работают")
        else:
            print("❌ Ошибка в слотах")
            return False

        # Тест рулетки
        won, msg, mult = roulette('color', 'red')
        if isinstance(won, bool) and isinstance(mult, float):
            print("✅ Рулетка работает")
        else:
            print("❌ Ошибка в рулетке")
            return False

        print("✅ Все игры протестированы успешно")
        return True

    except Exception as e:
        print(f"❌ Ошибка тестирования игр: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n⚙️ Проверка конфигурации...")

    # Проверка .env файла
    if os.path.exists('.env'):
        print("✅ Файл .env найден")

        from dotenv import load_dotenv
        load_dotenv()

        bot_token = os.getenv("BOT_TOKEN")
        admin_id = os.getenv("ADMIN_ID")

        if bot_token and bot_token != "YOUR_BOT_TOKEN_HERE":
            print("✅ BOT_TOKEN настроен")
        else:
            print("⚠️ BOT_TOKEN не настроен - получите токен у @BotFather")

        if admin_id and admin_id != "123456789":
            print("✅ ADMIN_ID настроен")
        else:
            print("⚠️ ADMIN_ID не настроен - укажите ваш Telegram ID")
    else:
        print("⚠️ Файл .env не найден")

    # Проверка зависимостей
    try:
        import aiogram
        print("✅ aiogram установлен")
    except ImportError:
        print("❌ aiogram не установлен")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv установлен")
    except ImportError:
        print("❌ python-dotenv не установлен")
        return False

    return True

def test_performance():
    """Тест производительности"""
    print("\n⚡ Тест производительности...")

    import time

    try:
        from bot import coinflip, dice, slots

        # Тест скорости игр
        start_time = time.time()
        for _ in range(1000):
            coinflip('heads')
            dice()
            slots()
        end_time = time.time()

        games_per_second = 3000 / (end_time - start_time)
        print(f"✅ Скорость игр: {games_per_second:.0f} игр/сек")

        # Тест базы данных
        from bot import Database
        db = Database()

        start_time = time.time()
        test_user = 888888888

        for i in range(100):
            db.create_user(test_user + i, f"test_user_{i}")
            db.update_balance(test_user + i, 100)
            db.add_game(test_user + i, "test", 100, 200, 2.0)

        end_time = time.time()
        operations_per_second = 300 / (end_time - start_time)
        print(f"✅ Скорость БД: {operations_per_second:.0f} операций/сек")

        # Очистка тестовых данных
        cursor = db.conn.cursor()
        for i in range(100):
            cursor.execute('DELETE FROM users WHERE user_id = ?', (test_user + i,))
            cursor.execute('DELETE FROM games WHERE user_id = ?', (test_user + i,))
        db.conn.commit()

        return True

    except Exception as e:
        print(f"❌ Ошибка теста производительности: {e}")
        return False

def show_statistics():
    """Показать статистику если бот уже работал"""
    print("\n📊 Статистика (если есть данные)...")

    if not os.path.exists('casino.db'):
        print("ℹ️ База данных пока не создана")
        return

    try:
        conn = sqlite3.connect('casino.db')
        c = conn.cursor()

        # Проверяем наличие данных
        users_count = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        games_count = c.execute('SELECT COUNT(*) FROM games').fetchone()[0]

        if users_count == 0:
            print("ℹ️ Пользователей пока нет")
        else:
            print(f"👥 Пользователей: {users_count}")
            print(f"🎮 Игр сыграно: {games_count}")

            # Популярные игры
            popular = c.execute('''
                SELECT game_type, COUNT(*) as count
                FROM games
                GROUP BY game_type
                ORDER BY count DESC
                LIMIT 3
            ''').fetchall()

            if popular:
                print("🏆 Популярные игры:")
                for game, count in popular:
                    print(f"  • {game}: {count} игр")

        conn.close()

    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")

def main():
    print("🎰 Тестирование Казино-Бота 🎰\n")

    results = []

    # Запускаем все тесты
    results.append(("Конфигурация", test_config()))
    results.append(("База данных", test_database()))
    results.append(("Игровые функции", test_games()))
    results.append(("Производительность", test_performance()))

    # Показываем статистику
    show_statistics()

    # Итоги
    print("\n" + "="*50)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("="*50)

    passed = 0
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1

    print(f"\nИтого: {passed}/{len(results)} тестов пройдено")

    if passed == len(results):
        print("\n🎉 Все тесты пройдены! Бот готов к запуску!")
        print("Запустите: python bot.py")
    else:
        print("\n⚠️ Есть проблемы. Проверьте настройки.")
        print("Инструкция: python run.py check")

if __name__ == "__main__":
    main()
