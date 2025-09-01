# Дополнительные игры для казино-бота
# Можно интегрировать в bot.py при необходимости

import secrets
import asyncio

def blackjack():
    """Блэкджек - простая версия"""
    player_cards = [secrets.randbelow(10) + 1, secrets.randbelow(10) + 1]
    dealer_cards = [secrets.randbelow(10) + 1, secrets.randbelow(10) + 1]

    player_sum = sum(player_cards)
    dealer_sum = sum(dealer_cards)

    # Упрощённая логика
    if player_sum > 21:
        return False, f"🃏 Вы: {player_sum} | Дилер: {dealer_sum}\nПеребор!", 0.0
    elif dealer_sum > 21 or player_sum > dealer_sum:
        return True, f"🃏 Вы: {player_sum} | Дилер: {dealer_sum}\nПобеда!", 2.0
    elif player_sum == dealer_sum:
        return True, f"🃏 Вы: {player_sum} | Дилер: {dealer_sum}\nНичья!", 1.0
    else:
        return False, f"🃏 Вы: {player_sum} | Дилер: {dealer_sum}\nПроигрыш!", 0.0

def crash():
    """Crash игра"""
    multiplier = 1.0
    crash_point = 1.0 + secrets.randbelow(500) / 100  # 1.0 - 6.0

    # Автоматический вывод в случайной точке
    auto_cashout = 1.0 + secrets.randbelow(300) / 100  # 1.0 - 4.0

    if auto_cashout < crash_point:
        return True, f"📈 Crash на {crash_point:.2f}x\nВывели на {auto_cashout:.2f}x!", auto_cashout
    else:
        return False, f"📈 Crash на {crash_point:.2f}x\nНе успели вывести!", 0.0

class JackpotManager:
    """Менеджер джекпота"""
    def __init__(self, db):
        self.db = db
        self.current_pot = 0
        self.entries = []

    def add_entry(self, user_id, bet):
        """Добавить ставку в джекпот"""
        self.db.conn.cursor().execute(
            'INSERT INTO jackpot_entries (user_id, bet) VALUES (?, ?)',
            (user_id, bet)
        )
        self.db.conn.commit()
        self.current_pot += bet
        self.entries.append((user_id, bet))

        # Если собралось достаточно ставок - разыграть
        if len(self.entries) >= 5:  # минимум 5 участников
            return self.draw_winner()
        return None

    def draw_winner(self):
        """Разыграть джекпот"""
        if not self.entries:
            return None

        # Взвешенная случайность (больше ставка = больше шансов)
        total_weight = sum(entry[1] for entry in self.entries)
        random_point = secrets.randbelow(total_weight)

        current_weight = 0
        for user_id, bet in self.entries:
            current_weight += bet
            if random_point < current_weight:
                # Победитель найден
                prize = self.current_pot
                self.db.update_balance(user_id, prize)

                # Очистка джекпота
                self.db.conn.cursor().execute('DELETE FROM jackpot_entries')
                self.db.conn.commit()
                self.current_pot = 0
                self.entries = []

                return user_id, prize

        return None

    def get_pot_info(self):
        """Информация о текущем джекпоте"""
        return {
            'pot': self.current_pot,
            'entries': len(self.entries),
            'participants': list(set(entry[0] for entry in self.entries))
        }

# Дополнительные функции для админа
def get_detailed_stats(db):
    """Подробная статистика для админа"""
    c = db.conn.cursor()

    # Статистика по играм
    game_stats = c.execute('''
        SELECT game_type, COUNT(*), SUM(bet), SUM(result), AVG(multiplier)
        FROM games
        GROUP BY game_type
    ''').fetchall()

    # Топ игроки по выигрышам
    top_winners = c.execute('''
        SELECT u.username, SUM(g.result - g.bet) as profit
        FROM users u
        JOIN games g ON u.user_id = g.user_id
        GROUP BY u.user_id
        ORDER BY profit DESC
        LIMIT 5
    ''').fetchall()

    # Активность по дням
    daily_activity = c.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as games_count
        FROM games
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    ''').fetchall()

    return {
        'games': game_stats,
        'top_winners': top_winners,
        'daily': daily_activity
    }

# Система анти-чит
class AntiCheat:
    @staticmethod
    def check_user_activity(db, user_id, timeframe_minutes=5):
        """Проверка подозрительной активности"""
        c = db.conn.cursor()
        recent_games = c.execute('''
            SELECT COUNT(*) FROM games
            WHERE user_id = ? AND created_at >= datetime('now', '-{} minutes')
        '''.format(timeframe_minutes), (user_id,)).fetchone()[0]

        return recent_games > 50  # Более 50 игр за 5 минут - подозрительно

    @staticmethod
    def check_win_rate(db, user_id, min_games=20):
        """Проверка подозрительного винрейта"""
        user = db.get_user(user_id)
        if not user or user[4] < min_games:  # total_games
            return False

        win_rate = user[5] / user[4]  # total_wins / total_games
        return win_rate > 0.8  # Винрейт более 80% подозрителен

# Дополнительные промокоды
SPECIAL_PROMOS = {
    'WELCOME2024': {'reward': 2000, 'max_uses': 100},
    'LUCKY777': {'reward': 777, 'max_uses': 50},
    'BIGWIN': {'reward': 5000, 'max_uses': 10},
    'NEWBIE': {'reward': 1500, 'max_uses': 200}
}

def create_special_promos(db):
    """Создать специальные промокоды"""
    for code, data in SPECIAL_PROMOS.items():
        db.create_promo(code, data['reward'], data['max_uses'])
    print("Специальные промокоды созданы!")

# Система достижений (можно добавить в БД)
ACHIEVEMENTS = {
    'first_win': {'name': 'Первая победа', 'reward': 100},
    'big_winner': {'name': 'Крупный выигрыш', 'reward': 500},  # выиграл >5000
    'lucky_streak': {'name': 'Везунчик', 'reward': 1000},     # 5 побед подряд
    'high_roller': {'name': 'Хайроллер', 'reward': 2000},     # ставка >1000
    'slots_master': {'name': 'Мастер слотов', 'reward': 300}, # 10 побед в слотах
    'jackpot_hunter': {'name': 'Охотник за джекпотом', 'reward': 1500}
}
