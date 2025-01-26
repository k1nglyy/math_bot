import sqlite3
import logging
from typing import Dict, List, Optional
import random
from sqlite3 import Error

logger = logging.getLogger(__name__)


def get_db():
    """Создает соединение с базой данных"""
    return sqlite3.connect('math_problems.db')


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
                solved INTEGER DEFAULT 0
            )
        ''')


def get_random_problem(exam_type: str, level: str) -> Optional[Dict]:
    """Получает случайную задачу из базы данных"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT topic, text, answer, hint, complexity
                FROM problems
                WHERE exam_type = ? AND level = ?
                ORDER BY RANDOM()
                LIMIT 1
                """,
                (exam_type, level.lower())
            )
            result = cursor.fetchone()

            if result:
                return {
                    "topic": result[0],
                    "text": result[1],
                    "answer": result[2],
                    "hint": result[3],
                    "exam_type": exam_type,
                    "level": level,
                    "complexity": result[4]
                }
            logger.warning(f"No problems found for {exam_type} {level}")
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


def update_user_stats(user_id: int, is_correct: bool):
    """Обновляет статистику пользователя

    Args:
        user_id (int): ID пользователя
        is_correct (bool): Правильный ли ответ
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # Создаем запись для пользователя, если её нет
            cursor.execute(
                """
                INSERT OR IGNORE INTO user_stats (user_id, total_attempts, solved)
                VALUES (?, 0, 0)
                """,
                (user_id,)
            )

            # Обновляем статистику в зависимости от правильности ответа
            if is_correct:
                cursor.execute(
                    """
                    UPDATE user_stats
                    SET total_attempts = total_attempts + 1,
                        solved = solved + 1
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
            else:
                cursor.execute(
                    """
                    UPDATE user_stats
                    SET total_attempts = total_attempts + 1
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )

            conn.commit()
            logger.info(f"Updated stats for user {user_id}: correct={is_correct}")
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")


def get_user_stats(user_id: int) -> Dict:
    """Получает статистику пользователя"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # Создаем запись для пользователя, если её нет
            cursor.execute(
                """
                INSERT OR IGNORE INTO user_stats (user_id, total_attempts, solved)
                VALUES (?, 0, 0)
                """,
                (user_id,)
            )

            cursor.execute(
                """
                SELECT total_attempts, solved
                FROM user_stats
                WHERE user_id = ?
                """,
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                total_attempts, solved = result
                return {
                    "total_attempts": total_attempts,
                    "solved": solved,
                    "accuracy": round((solved / total_attempts * 100) if total_attempts > 0 else 0, 1)
                }
            return {
                "total_attempts": 0,
                "solved": 0,
                "accuracy": 0.0
            }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return {
            "total_attempts": 0,
            "solved": 0,
            "accuracy": 0.0
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


if __name__ == "__main__":
    create_tables()
    add_sample_problems()
    problem = get_random_problem("ЕГЭ", "база")
    print("Случайная задача:", problem)