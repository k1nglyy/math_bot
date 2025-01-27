import sqlite3
import logging
from typing import Dict, List, Optional
import random
from sqlite3 import Error
from pathlib import Path
import math

logger = logging.getLogger(__name__)

# Определяем путь к базе данных
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "math_problems.db"


def get_db():
    """Создает соединение с базой данных"""
    # Создаем директорию data, если её нет
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Инициализирует базу данных"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                topic TEXT NOT NULL,
                text TEXT NOT NULL,
                answer TEXT NOT NULL,
                exam_type TEXT NOT NULL,
                level TEXT NOT NULL,
                complexity INTEGER NOT NULL,
                hint TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                total_attempts INTEGER DEFAULT 0,
                solved INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
            )
        ''')

        # Новая таблица для достижений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_value INTEGER NOT NULL,
                icon TEXT NOT NULL
            )
        ''')

        # Таблица для хранения полученных достижений пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id INTEGER,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id)
            )
        ''')

        # Добавляем базовые достижения, если их нет
        cursor.execute(
            'INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value, icon) VALUES (?, ?, ?, ?, ?)',
            ("Первые шаги", "Решите первую задачу", "solved", 1, "🎯"))
        cursor.execute(
            'INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value, icon) VALUES (?, ?, ?, ?, ?)',
            ("Начинающий математик", "Решите 10 задач", "solved", 10, "🎓"))
        cursor.execute(
            'INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value, icon) VALUES (?, ?, ?, ?, ?)',
            ("Опытный решатель", "Решите 50 задач", "solved", 50, "🏆"))
        cursor.execute(
            'INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value, icon) VALUES (?, ?, ?, ?, ?)',
            ("Мастер математики", "Решите 100 задач", "solved", 100, "👑"))
        cursor.execute(
            'INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value, icon) VALUES (?, ?, ?, ?, ?)',
            ("Точность 80%", "Достигните точности решения 80%", "accuracy", 80, "🎯"))
        cursor.execute(
            'INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value, icon) VALUES (?, ?, ?, ?, ?)',
            ("Точность 90%", "Достигните точности решения 90%", "accuracy", 90, "🎯"))


def get_random_problem(exam_type: str, level: str, last_topic: str = None) -> Optional[Dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            if last_topic:
                # Выбираем задачу с другой темой
                cursor.execute(
                    """
                    SELECT topic, text, answer, hint, complexity
                    FROM problems
                    WHERE exam_type = ? 
                    AND level = ?
                    AND topic != ?
                    ORDER BY RANDOM()
                    LIMIT 1
                    """,
                    (exam_type, level, last_topic)
                )
            else:
                # Если это первая задача, выбираем любую
                cursor.execute(
                    """
                    SELECT topic, text, answer, hint, complexity
                    FROM problems
                    WHERE exam_type = ? 
                    AND level = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                    """,
                    (exam_type, level)
                )

            result = cursor.fetchone()

            if result:
                return {
                    "topic": result[0],
                    "text": result[1],
                    "answer": result[2],
                    "hint": result[3],
                    "complexity": result[4]
                }
            return None
    except Exception as e:
        logger.error(f"Error getting random problem: {e}")
        return None


def add_bulk_problems(problems: List[Dict]):
    """Добавляет список задач в базу данных"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT INTO problems (topic, text, answer, exam_type, level, complexity, hint)
                VALUES (:topic, :text, :answer, :exam_type, :level, :complexity, :hint)
                """,
                problems
            )
            logger.info(f"Added {len(problems)} problems to database")
    except Exception as e:
        logger.error(f"Error adding problems: {e}")


def get_user_level(solved: int, accuracy: float) -> dict:
    """Определяет уровень и звание пользователя"""

    # Базовые очки опыта
    xp = solved * 10

    # Бонус за точность
    if accuracy >= 90:
        xp *= 1.5
    elif accuracy >= 80:
        xp *= 1.3
    elif accuracy >= 70:
        xp *= 1.2

    # Определение уровня (каждый следующий уровень требует на 20% больше опыта)
    level = int(math.log(xp / 100 + 1, 1.2)) + 1 if xp > 0 else 1

    # Звания в зависимости от уровня и точности
    ranks = {
        (1, 0): "🌱 Новичок",
        (3, 0): "📚 Ученик",
        (5, 70): "🎯 Практик",
        (8, 75): "💫 Знаток",
        (12, 80): "🏆 Мастер",
        (15, 85): "👑 Гроссмейстер",
        (20, 90): "⭐ Легенда",
        (25, 95): "🌟 Профессор"
    }

    current_rank = "🌱 Новичок"
    for (req_level, req_accuracy), rank in sorted(ranks.items()):
        if level >= req_level and accuracy >= req_accuracy:
            current_rank = rank

    # Расчет прогресса до следующего уровня
    next_level_xp = 100 * (1.2 ** (level - 1))
    current_level_xp = 100 * (1.2 ** (level - 2)) if level > 1 else 0
    progress = int((xp - current_level_xp) / (next_level_xp - current_level_xp) * 100)

    return {
        "level": level,
        "rank": current_rank,
        "xp": int(xp),
        "next_level_xp": int(next_level_xp),
        "progress": progress
    }


def update_user_stats(user_id: int, is_correct: bool) -> None:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_stats (user_id, total_attempts, solved)
                VALUES (?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    total_attempts = total_attempts + 1,
                    solved = solved + ?
                """,
                (user_id, 1 if is_correct else 0, 1 if is_correct else 0)
            )

            # Обновляем XP пользователя
            if is_correct:
                cursor.execute(
                    """
                    UPDATE user_stats 
                    SET xp = xp + ? 
                    WHERE user_id = ?
                    """,
                    (10, user_id)
                )
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")


def get_user_stats(user_id: int) -> Dict:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT total_attempts, solved, xp
                FROM user_stats
                WHERE user_id = ?
                """,
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                total_attempts, solved, xp = result
                accuracy = round((solved / total_attempts * 100) if total_attempts > 0 else 0, 1)
                level_info = get_user_level(solved, accuracy)

                return {
                    "total_attempts": total_attempts,
                    "solved": solved,
                    "accuracy": accuracy,
                    "xp": xp,
                    "level": level_info["level"],
                    "rank": level_info["rank"],
                    "next_level_xp": level_info["next_level_xp"],
                    "progress": level_info["progress"]
                }
            return {
                "total_attempts": 0,
                "solved": 0,
                "accuracy": 0.0,
                "xp": 0,
                "level": 1,
                "rank": "🌱 Новичок",
                "next_level_xp": 100,
                "progress": 0
            }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return {
            "total_attempts": 0,
            "solved": 0,
            "accuracy": 0.0,
            "xp": 0,
            "level": 1,
            "rank": "🌱 Новичок",
            "next_level_xp": 100,
            "progress": 0
        }


def create_tables():
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY,
                    topic TEXT NOT NULL,
                    text TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    exam_type TEXT NOT NULL,
                    level TEXT NOT NULL,
                    complexity INTEGER DEFAULT 1,
                    hint TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    solved INTEGER DEFAULT 0,
                    total_attempts INTEGER DEFAULT 0,
                    correct_streak INTEGER DEFAULT 0,
                    max_streak INTEGER DEFAULT 0,
                    last_active TEXT,
                    algebra_solved INTEGER DEFAULT 0,
                    geometry_solved INTEGER DEFAULT 0,
                    probability_solved INTEGER DEFAULT 0,
                    statistics_solved INTEGER DEFAULT 0,
                    ege_solved INTEGER DEFAULT 0,
                    oge_solved INTEGER DEFAULT 0,
                    base_level_solved INTEGER DEFAULT 0,
                    profile_level_solved INTEGER DEFAULT 0,
                    easy_solved INTEGER DEFAULT 0,
                    medium_solved INTEGER DEFAULT 0,
                    hard_solved INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    achievement_type TEXT NOT NULL,
                    achieved_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solution_history (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    problem_id INTEGER,
                    is_correct BOOLEAN,
                    attempt_time TEXT,
                    solution_time INTEGER,
                    FOREIGN KEY (user_id) REFERENCES user_stats (user_id),
                    FOREIGN KEY (problem_id) REFERENCES problems (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problem_timing_stats (
                    id INTEGER PRIMARY KEY,
                    problem_id INTEGER,
                    avg_solution_time REAL,
                    total_attempts INTEGER,
                    success_rate REAL,
                    FOREIGN KEY (problem_id) REFERENCES problems (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_difficulty_level (
                    user_id INTEGER PRIMARY KEY,
                    topic TEXT,
                    current_difficulty REAL DEFAULT 1.0,
                    last_updated TEXT,
                    success_rate REAL,
                    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exam_level 
                ON problems (exam_type, level)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_topic 
                ON problems (topic)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_solution_user 
                ON solution_history (user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_achievements_user 
                ON achievements (user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_complexity 
                ON problems (complexity)
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timing_problem ON problem_timing_stats (problem_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_difficulty_user ON user_difficulty_level (user_id, topic)')
            conn.commit()
    except Error as e:
        print(f"Ошибка при создании таблиц: {e}")


def add_sample_problems():
    """Добавляет примеры задач в базу данных"""
    sample_problems = [
        {
            "topic": "Алгебра",
            "text": r"Решите уравнение: \( x^2 - 5x + 6 = 0 \).",
            "answer": "2;3",
            "exam_type": "ЕГЭ",
            "level": "база",
            "complexity": 2,
            "hint": r"D = 5² - 4·6 = 25 - 24 = 1"
        },
        {
            "topic": "Геометрия",
            "text": r"Найдите площадь круга с радиусом 3 см.",
            "answer": "28.27",
            "exam_type": "ОГЭ",
            "level": "база",
            "complexity": 1,
            "hint": r"Формула площади круга: \( S = \pi r^2 \)."
        },
        {
            "topic": "Теория вероятностей",
            "text": r"Вероятность события A равна 0.3. Найдите вероятность противоположного события.",
            "answer": "0.7; 7/10",
            "exam_type": "ЕГЭ",
            "level": "база",
            "complexity": 1,
            "hint": r"Вероятность противоположного события: \( P(\overline{A}) = 1 - P(A) \)"
        },
        {
            "topic": "Статистика",
            "text": r"Найдите среднее арифметическое чисел: 2, 4, 6, 8, 10",
            "answer": "6",
            "exam_type": "ОГЭ",
            "level": "база",
            "complexity": 1,
            "hint": r"Среднее = (2 + 4 + 6 + 8 + 10) ÷ 5 = 30 ÷ 5 = 6"
        }
    ]

    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR IGNORE INTO problems 
                (topic, text, answer, exam_type, level, complexity, hint)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [(p['topic'], p['text'], p['answer'], p['exam_type'],
                   p['level'], p['complexity'], p['hint']) for p in sample_problems])
            conn.commit()
    except Error as e:
        print(f"Ошибка при добавлении примеров задач: {e}")


def update_problem_timing(problem_id: int, solution_time: int, is_correct: bool):
    """Обновляет статистику времени решения задачи"""
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()

            # Создаем или обновляем статистику времени решения
            cursor.execute('''
                INSERT INTO problem_timing_stats (problem_id, avg_solution_time, total_attempts, success_rate)
                VALUES (?, ?, 1, ?)
                ON CONFLICT (problem_id) DO UPDATE SET
                    avg_solution_time = (
                        (avg_solution_time * total_attempts + ?) / (total_attempts + 1)
                    ),
                    total_attempts = total_attempts + 1,
                    success_rate = (
                        (success_rate * total_attempts + ?) / (total_attempts + 1)
                    )
            ''', (problem_id, solution_time, 1 if is_correct else 0, solution_time, 1 if is_correct else 0))

            conn.commit()
    except Error as e:
        print(f"Ошибка при обновлении статистики времени: {e}")


def update_user_difficulty(user_id: int, topic: str, is_correct: bool):
    """Обновляет уровень сложности для пользователя по теме"""
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()

            # Получаем текущий уровень сложности
            cursor.execute('''
                INSERT INTO user_difficulty_level (user_id, topic, current_difficulty, last_updated, success_rate)
                VALUES (?, ?, 1.0, datetime('now'), 0.5)
                ON CONFLICT (user_id) DO UPDATE SET
                    current_difficulty = CASE
                        WHEN ? THEN MIN(current_difficulty * 1.1, 5.0)  -- Увеличиваем сложность при успехе
                        ELSE MAX(current_difficulty * 0.9, 1.0)  -- Уменьшаем при неудаче
                    END,
                    last_updated = datetime('now'),
                    success_rate = (success_rate * 9 + ?) / 10  -- Скользящее среднее
            ''', (user_id, topic, is_correct, 1 if is_correct else 0))

            conn.commit()
    except Error as e:
        print(f"Ошибка при обновлении сложности: {e}")


def get_appropriate_difficulty(user_id: int, topic: str) -> float:
    """Получает подходящий уровень сложности для пользователя"""
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT current_difficulty, success_rate
                FROM user_difficulty_level
                WHERE user_id = ? AND topic = ?
            ''', (user_id, topic))

            result = cursor.fetchone()
            if result:
                difficulty, success_rate = result
                # Корректируем сложность на основе успеваемости
                if success_rate > 0.8:  # Слишком легко
                    return min(difficulty * 1.2, 5.0)
                elif success_rate < 0.4:  # Слишком сложно
                    return max(difficulty * 0.8, 1.0)
                return difficulty
            return 1.0  # Начальный уровень сложности
    except Error as e:
        print(f"Ошибка при получении уровня сложности: {e}")
        return 1.0


def check_achievements(user_id: int) -> List[Dict]:
    """Проверяет и возвращает новые достижения пользователя"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Получаем статистику пользователя
            stats = get_user_stats(user_id)

            # Получаем все достижения, которых еще нет у пользователя
            cursor.execute('''
                SELECT a.id, a.name, a.description, a.condition_type, a.condition_value, a.icon
                FROM achievements a
                LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
                WHERE ua.user_id IS NULL
            ''', (user_id,))

            new_achievements = []
            for achievement in cursor.fetchall():
                aid, name, description, condition_type, condition_value, icon = achievement

                # Проверяем условия достижения
                if condition_type == "solved" and stats["solved"] >= condition_value:
                    new_achievements.append({
                        "name": name,
                        "description": description,
                        "icon": icon
                    })
                    # Записываем полученное достижение
                    cursor.execute('''
                        INSERT INTO user_achievements (user_id, achievement_id)
                        VALUES (?, ?)
                    ''', (user_id, aid))

                elif condition_type == "accuracy" and stats["accuracy"] >= condition_value:
                    new_achievements.append({
                        "name": name,
                        "description": description,
                        "icon": icon
                    })
                    # Записываем полученное достижение
                    cursor.execute('''
                        INSERT INTO user_achievements (user_id, achievement_id)
                        VALUES (?, ?)
                    ''', (user_id, aid))

            conn.commit()
            return new_achievements

    except Exception as e:
        logger.error(f"Error checking achievements: {e}")
        return []


def get_user_achievements(user_id: int) -> List[Dict]:
    """Получает все достижения пользователя"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.name, a.description, a.icon, ua.obtained_at
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = ?
                ORDER BY ua.obtained_at DESC
            ''', (user_id,))

            return [{
                "name": name,
                "description": desc,
                "icon": icon,
                "obtained_at": obtained_at
            } for name, desc, icon, obtained_at in cursor.fetchall()]

    except Exception as e:
        logger.error(f"Error getting user achievements: {e}")
        return []


def get_adaptive_problem(exam_type: str, level: str, last_topic: str = None, user_stats: dict = None) -> Optional[Dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Определяем оптимальную сложность на основе статистики
            if user_stats and user_stats['total_attempts'] > 0:
                accuracy = user_stats['accuracy']
                solved = user_stats['solved']

                # Адаптивная логика сложности с учетом количества решенных задач
                if exam_type == "ЕГЭ" and level == "профиль":
                    if solved < 3:  # Первые 3 задачи
                        target_complexity = 1
                    elif accuracy >= 80 and solved >= 3:
                        target_complexity = random.choice([2, 3])  # Чередуем сложные и средние
                    elif accuracy >= 60:
                        target_complexity = 2
                    else:
                        target_complexity = 1

                elif exam_type == "ЕГЭ" and level == "база":
                    if solved < 3:  # Первые 3 задачи
                        target_complexity = 1
                    elif accuracy >= 85 and solved >= 3:
                        target_complexity = 2
                    elif accuracy >= 70:
                        target_complexity = random.choice([1, 2])
                    else:
                        target_complexity = 1

                else:  # ОГЭ
                    if solved < 3:  # Первые 3 задачи
                        target_complexity = 1
                    elif accuracy >= 80 and solved >= 3:
                        target_complexity = 2
                    else:
                        target_complexity = 1
            else:
                target_complexity = 1

            # Логика выбора задачи
            query_params = [exam_type, level]
            base_query = """
                SELECT topic, text, answer, hint, complexity
                FROM problems
                WHERE exam_type = ? 
                AND level = ?
            """

            if last_topic:
                base_query += " AND topic != ?"
                query_params.append(last_topic)

            # Сначала пытаемся найти задачу нужной сложности
            full_query = base_query + " AND complexity = ? ORDER BY RANDOM() LIMIT 1"
            query_params.append(target_complexity)

            cursor.execute(full_query, query_params)
            result = cursor.fetchone()

            # Если не нашли задачу нужной сложности, берем любую подходящую
            if not result:
                cursor.execute(base_query + " ORDER BY RANDOM() LIMIT 1", query_params[:-1])
                result = cursor.fetchone()

            if result:
                return {
                    "topic": result[0],
                    "text": result[1],
                    "answer": result[2],
                    "hint": result[3],
                    "complexity": result[4]
                }
            return None

    except Exception as e:
        logger.error(f"Error getting adaptive problem: {e}")
        return None


if __name__ == "__main__":
    create_tables()
    add_sample_problems()
    problem = get_random_problem("ЕГЭ", "база")
    print("Случайная задача:", problem)