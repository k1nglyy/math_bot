import sqlite3


def create_tables():
    conn = sqlite3.connect('data/problems.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            exam_type TEXT,
            level TEXT,
            score INTEGER DEFAULT 0
        )
    ''')

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
    conn.commit()
    conn.close()


def get_random_problem(exam_type: str, level: str) -> dict:
    conn = sqlite3.connect('data/problems.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM problems 
        WHERE exam_type = ? AND level = ?
        ORDER BY RANDOM() 
        LIMIT 1
    ''', (exam_type, level))
    problem = cursor.fetchone()
    conn.close()

    if not problem:
        return None

    return {
        "id": problem[0],
        "topic": problem[1],
        "text": problem[2],
        "answer": problem[3],
        "exam_type": problem[4],
        "level": problem[5],
        "hint": problem[7]
    }


def add_sample_problems():
    conn = sqlite3.connect('data/problems.db')
    cursor = conn.cursor()

    problems = [
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

    cursor.executemany('''
        INSERT INTO problems (topic, text, answer, exam_type, level, complexity, hint)
        VALUES (:topic, :text, :answer, :exam_type, :level, :complexity, :hint)
    ''', problems)
    conn.commit()
    conn.close()

def add_bulk_problems(problems: list):
    conn = sqlite3.connect('data/problems.db')
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO problems (topic, text, answer, exam_type, level, complexity, hint)
        VALUES (:topic, :text, :answer, :exam_type, :level, :complexity, :hint)
    ''', problems)
    conn.commit()
    conn.close()