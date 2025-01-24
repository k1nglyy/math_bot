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
                    last_active TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exam_level 
                ON problems (exam_type, level)
            ''')
            conn.commit()
    except Error as e:
        print(f"Ошибка при создании таблиц: {e}")

def get_random_problem(exam_type: str, level: str) -> dict:
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM problems 
                WHERE exam_type = ? AND level = ?
                ORDER BY RANDOM() 
                LIMIT 1
            ''', (exam_type, level))
            problem = cursor.fetchone()
            return {
                "id": problem[0],
                "topic": problem[1],
                "text": problem[2],
                "answer": problem[3],
                "exam_type": problem[4],
                "level": problem[5],
                "hint": problem[7]
            } if problem else None
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
    sample_problems = [
        {
            "topic": "Алгебра",
            "text": r"Решите уравнение: \( x^2 - 5x + 6 = 0 \).",
            "answer": "2;3",
            "exam_type": "ЕГЭ",
            "level": "база",
            "complexity": 2,
            "hint": r"Используйте теорему Виета."
        },
        {
            "topic": "Геометрия",
            "text": r"Найдите площадь круга с радиусом 3 см.",
            "answer": "28.27",
            "exam_type": "ОГЭ",
            "level": "база",
            "complexity": 1,
            "hint": r"Формула площади круга: \( S = \pi r^2 \)."
        }
    ]
    add_bulk_problems(sample_problems)

def update_user_stats(user_id: int):
    try:
        with sqlite3.connect('data/problems.db') as conn:
            cursor = conn.cursor()
            # Добавление пользователя, если его нет
            cursor.execute('''
                INSERT OR IGNORE INTO user_stats (user_id, solved) 
                VALUES (?, 0)
            ''', (user_id,))
            cursor.execute('''
                UPDATE user_stats 
                SET solved = solved + 1, last_active = datetime('now') 
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
    except Error as e:
        print(f"Ошибка при обновлении статистики: {e}")


if __name__ == "__main__":
    create_tables()
    add_sample_problems()
    problem = get_random_problem("ЕГЭ", "база")
    print("Случайная задача:", problem)