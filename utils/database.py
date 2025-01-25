import sqlite3
from sqlite3 import Error

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

def get_random_problem(exam_type: str, level: str, user_id: int = None) -> dict:
    """Получает случайную задачу с учетом уровня пользователя"""
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT p.* 
                    FROM problems p
                    WHERE p.exam_type = ? AND p.level = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                ''', (exam_type, level))
            else:
                cursor.execute('''
                    SELECT * 
                    FROM problems 
                    WHERE exam_type = ? AND level = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                ''', (exam_type, level))
            
            problem = cursor.fetchone()
            if problem:
                return {
                    "id": problem[0],
                    "topic": problem[1],
                    "text": problem[2],
                    "answer": problem[3],
                    "exam_type": problem[4],
                    "level": problem[5],
                    "complexity": problem[6],
                    "hint": problem[7]
                }
            return None
    except Error as e:
        print(f"Ошибка при получении задачи: {e}")
        return None

def add_bulk_problems(problems: list):
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO problems 
                (topic, text, answer, exam_type, level, complexity, hint)
                VALUES (:topic, :text, :answer, :exam_type, :level, :complexity, :hint)
            ''', problems)
            conn.commit()
    except Error as e:
        print(f"Ошибка при добавлении задач: {e}")

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

def update_user_stats(user_id: int, problem: dict, is_correct: bool, solution_time: int = None):
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO user_stats 
                (user_id, solved, total_attempts, correct_streak, max_streak, last_active)
                VALUES (?, 0, 0, 0, 0, datetime('now'))
            ''', (user_id,))
            
            if is_correct:
                cursor.execute('''
                    UPDATE user_stats 
                    SET solved = solved + 1,
                        total_attempts = total_attempts + 1,
                        correct_streak = correct_streak + 1,
                        max_streak = CASE 
                            WHEN correct_streak + 1 > max_streak 
                            THEN correct_streak + 1 
                            ELSE max_streak 
                        END,
                        last_active = datetime('now'),
                        algebra_solved = CASE 
                            WHEN ? = 'Алгебра' THEN algebra_solved + 1 
                            ELSE algebra_solved 
                        END,
                        geometry_solved = CASE 
                            WHEN ? = 'Геометрия' THEN geometry_solved + 1 
                            ELSE geometry_solved 
                        END,
                        probability_solved = CASE 
                            WHEN ? = 'Теория вероятностей' THEN probability_solved + 1 
                            ELSE probability_solved 
                        END,
                        statistics_solved = CASE 
                            WHEN ? = 'Статистика' THEN statistics_solved + 1 
                            ELSE statistics_solved 
                        END,
                        ege_solved = CASE 
                            WHEN ? = 'ЕГЭ' THEN ege_solved + 1 
                            ELSE ege_solved 
                        END,
                        oge_solved = CASE 
                            WHEN ? = 'ОГЭ' THEN oge_solved + 1 
                            ELSE oge_solved 
                        END,
                        base_level_solved = CASE 
                            WHEN ? = 'база' THEN base_level_solved + 1 
                            ELSE base_level_solved 
                        END,
                        profile_level_solved = CASE 
                            WHEN ? = 'профиль' THEN profile_level_solved + 1 
                            ELSE profile_level_solved 
                        END,
                        easy_solved = CASE 
                            WHEN ? <= 2 THEN easy_solved + 1 
                            ELSE easy_solved 
                        END,
                        medium_solved = CASE 
                            WHEN ? = 3 THEN medium_solved + 1 
                            ELSE medium_solved 
                        END,
                        hard_solved = CASE 
                            WHEN ? >= 4 THEN hard_solved + 1 
                            ELSE hard_solved 
                        END
                    WHERE user_id = ?
                ''', (problem['topic'], problem['topic'], problem['topic'], 
                     problem['topic'], problem['exam_type'], problem['exam_type'],
                     problem['level'], problem['level'], problem['complexity'],
                     problem['complexity'], problem['complexity'], user_id))
            else:
                cursor.execute('''
                    UPDATE user_stats 
                    SET total_attempts = total_attempts + 1,
                        correct_streak = 0,
                        last_active = datetime('now')
                    WHERE user_id = ?
                ''', (user_id,))
            
            cursor.execute('''
                INSERT INTO solution_history 
                (user_id, problem_id, is_correct, attempt_time, solution_time)
                VALUES (?, ?, ?, datetime('now'), ?)
            ''', (user_id, problem['id'], is_correct, solution_time))
            
            conn.commit()
            
            check_and_award_achievements(cursor, user_id)
            
    except Error as e:
        print(f"Ошибка при обновлении статистики: {e}")

def get_user_stats(user_id: int) -> dict:
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT solved, total_attempts, correct_streak, max_streak,
                       last_active, algebra_solved, geometry_solved,
                       probability_solved, statistics_solved,
                       ege_solved, oge_solved, base_level_solved,
                       profile_level_solved, easy_solved, medium_solved,
                       hard_solved
                FROM user_stats 
                WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            cursor.execute('''
                SELECT achievement_type, achieved_at
                FROM achievements
                WHERE user_id = ?
                ORDER BY achieved_at DESC
            ''', (user_id,))
            achievements = cursor.fetchall()
            
            if result:
                return {
                    "solved": result[0],
                    "total_attempts": result[1],
                    "correct_streak": result[2],
                    "max_streak": result[3],
                    "last_active": result[4],
                    "topics": {
                        "Алгебра": result[5],
                        "Геометрия": result[6],
                        "Теория вероятностей": result[7],
                        "Статистика": result[8]
                    },
                    "exam_types": {
                        "ЕГЭ": result[9],
                        "ОГЭ": result[10]
                    },
                    "levels": {
                        "база": result[11],
                        "профиль": result[12]
                    },
                    "complexity": {
                        "легкие": result[13],
                        "средние": result[14],
                        "сложные": result[15]
                    },
                    "achievements": [
                        {"type": ach[0], "date": ach[1]} for ach in achievements
                    ]
                }
            return {
                "solved": 0,
                "total_attempts": 0,
                "correct_streak": 0,
                "max_streak": 0,
                "last_active": None,
                "topics": {
                    "Алгебра": 0,
                    "Геометрия": 0,
                    "Теория вероятностей": 0,
                    "Статистика": 0
                },
                "exam_types": {
                    "ЕГЭ": 0,
                    "ОГЭ": 0
                },
                "levels": {"база": 0, "профиль": 0},
                "complexity": {"легкие": 0, "средние": 0, "сложные": 0},
                "achievements": []
            }
    except Error as e:
        print(f"Ошибка при получении статистики: {e}")
        return None

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