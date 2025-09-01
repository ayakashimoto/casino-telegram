# Дополнительные настройки казино-бота

# Игровые настройки
GAME_SETTINGS = {
    'min_bet': 100,
    'max_bet': 10000,
    'daily_bonus': 500,
    'start_balance': 1000,
    'max_games_per_minute': 10,  # Анти-спам
}

# Коэффициенты выплат
PAYOUTS = {
    'coinflip': 2.0,
    'dice': {
        6: 5.0,
        'high': 2.0,  # 4-5
        'low': 0.0    # 1-3
    },
    'slots': {
        'triple': 10.0,
        'double': 3.0,
        'nothing': 0.0
    },
    'roulette': {
        'number': 36.0,
        'color': 2.0,
        'even_odd': 2.0
    },
    'blackjack': 2.0,
    'crash_max': 100.0
}

# Символы для слотов
SLOT_SYMBOLS = ['🍎', '🍊', '🍇', '🍋', '🍒', '⭐', '💎', '🔔']

# Тексты сообщений
MESSAGES = {
    'welcome': """🎰 *Добро пожаловать в Казино\\-Бот\\!* 🎰

💰 Стартовый баланс: {balance} очков
🎮 7 захватывающих игр
🎁 Ежедневные бонусы
🏆 Соревнуйтесь в рейтинге\\!

Удачи в игре\\! 🍀""",

    'insufficient_funds': "❌ *Недостаточно средств\\!*\n💰 Ваш баланс: {balance} очков",
    'min_bet_error': "❌ *Минимальная ставка {min_bet} очков\\!*",
    'max_bet_error': "❌ *Максимальная ставка {max_bet} очков\\!*",

    'bonus_claimed': """🎁 *Ежедневный бонус получен\\!* 🎁

💰 \\+{bonus} очков к балансу\\!
💳 Новый баланс: {balance} очков
⏰ Следующий бонус через 24 часа""",

    'bonus_already_claimed': """🎁 *Ежедневный бонус* 🎁

❌ Бонус уже получен сегодня
⏰ Возвращайтесь завтра за новым бонусом\\!
💰 Текущий баланс: {balance} очков""",

    'game_win': "🎉 *ВЫИГРЫШ\\!* 🎉\n💰 \\+{amount} очков",
    'game_lose': "😔 *Неудача\\!*\n💸 \\-{amount} очков",

    'promo_success': "✅ *Промокод активирован\\!*\n💰 \\+{reward} очков",
    'promo_not_found': "❌ *Промокод не найден*",
    'promo_used': "❌ *Промокод уже использован*",
    'promo_expired': "❌ *Промокод исчерпан*"
}

# Эмодзи для рейтинга
RATING_MEDALS = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
    4: "🏅",
    5: "🎖️"
}

# Настройки рулетки
ROULETTE_COLORS = {
    0: 'green',
    # Красные числа
    **{i: 'red' for i in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]},
    # Чёрные числа
    **{i: 'black' for i in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]}
}

# Настройки анти-чит системы
ANTI_CHEAT = {
    'max_games_per_hour': 200,
    'max_win_rate': 0.85,  # 85% максимальный винрейт
    'min_games_for_check': 20,
    'suspicious_patterns': {
        'same_bet_count': 50,  # одинаковая ставка 50 раз подряд
        'rapid_fire': 5,       # 5 игр за 10 секунд
    }
}

# Промокоды по умолчанию
DEFAULT_PROMOS = {
    'START2024': {'reward': 1000, 'max_uses': 1000},
    'WELCOME': {'reward': 500, 'max_uses': 500},
    'LUCKY777': {'reward': 777, 'max_uses': 77},
    'BIGBONUS': {'reward': 2000, 'max_uses': 100},
    'NEWBIE': {'reward': 1500, 'max_uses': 200},
    'WEEKEND': {'reward': 800, 'max_uses': 300},
    'SLOTS': {'reward': 600, 'max_uses': 150},
    'ROULETTE': {'reward': 900, 'max_uses': 150},
    'PREMIUM': {'reward': 5000, 'max_uses': 50}
}

# Настройки джекпота
JACKPOT_SETTINGS = {
    'min_participants': 3,
    'min_bet': 500,
    'auto_draw_threshold': 10,  # автоматический розыгрыш при 10 участниках
    'commission': 0.05  # 5% комиссия казино
}

# Уровни VIP статуса (будущее расширение)
VIP_LEVELS = {
    0: {'name': 'Новичок', 'min_balance': 0, 'bonus_multiplier': 1.0},
    1: {'name': 'Бронза', 'min_balance': 10000, 'bonus_multiplier': 1.2},
    2: {'name': 'Серебро', 'min_balance': 50000, 'bonus_multiplier': 1.5},
    3: {'name': 'Золото', 'min_balance': 100000, 'bonus_multiplier': 2.0},
    4: {'name': 'Платина', 'min_balance': 500000, 'bonus_multiplier': 3.0},
    5: {'name': 'Алмаз', 'min_balance': 1000000, 'bonus_multiplier': 5.0}
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'casino_bot.log',
    'max_bytes': 10*1024*1024,  # 10MB
    'backup_count': 5
}

# Тайминги игр (в секундах)
GAME_TIMINGS = {
    'slots_animation': 0.5,
    'roulette_spin': 2.0,
    'crash_update': 0.1,
    'blackjack_deal': 1.0
}

# Математические настройки
PROBABILITY_SETTINGS = {
    'dice': {
        'six_chance': 1/6,
        'high_chance': 2/6,  # 4-5
        'low_chance': 3/6    # 1-3
    },
    'slots': {
        'triple_chance': 0.02,   # 2%
        'double_chance': 0.15,   # 15%
        'nothing_chance': 0.83   # 83%
    },
    'crash': {
        'min_multiplier': 1.01,
        'max_multiplier': 100.0,
        'crash_probability': 0.99  # 99% шанс краша
    }
}

# Цвета для веб-интерфейса (если будет добавлен)
UI_COLORS = {
    'primary': '#FFD700',      # Золотой
    'secondary': '#FF6B6B',    # Красный
    'success': '#4ECDC4',      # Бирюзовый
    'danger': '#FF4757',       # Красный
    'warning': '#FFA726',      # Оранжевый
    'info': '#5DADE2',         # Голубой
    'dark': '#2F3542',         # Тёмный
    'light': '#F1F2F6'         # Светлый
}

# Статистика для админа
ADMIN_STATS_QUERIES = {
    'daily_revenue': """
        SELECT DATE(created_at) as date,
               SUM(bet) as total_bets,
               SUM(result) as total_payouts,
               SUM(bet) - SUM(result) as profit
        FROM games
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """,

    'popular_games': """
        SELECT game_type,
               COUNT(*) as games_count,
               AVG(bet) as avg_bet,
               SUM(bet) as total_bets,
               SUM(result) as total_payouts
        FROM games
        GROUP BY game_type
        ORDER BY games_count DESC
    """,

    'active_users': """
        SELECT u.username,
               u.balance,
               COUNT(g.id) as games_played,
               SUM(g.bet) as total_bet,
               SUM(g.result) as total_won
        FROM users u
        LEFT JOIN games g ON u.user_id = g.user_id
        WHERE g.created_at >= datetime('now', '-7 days')
        GROUP BY u.user_id
        ORDER BY games_played DESC
        LIMIT 20
    """
}
