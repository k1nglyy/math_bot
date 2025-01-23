import aiosqlite
import os
from pathlib import Path
from typing import Optional, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'problems.db'

async def init_db():
    (BASE_DIR / 'data').mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                exam TEXT NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                solution TEXT NOT NULL,
                difficulty INTEGER DEFAULT 1
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                algebra_solved INTEGER DEFAULT 0,
                geometry_solved INTEGER DEFAULT 0
            )
        ''')
        await conn.commit()

async def get_problem_by_params(exam: str, topic: str) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            '''SELECT * FROM problems 
            WHERE exam = ? AND topic = ? 
            ORDER BY RANDOM() LIMIT 1''',
            (exam, topic)
        )
        problem = await cursor.fetchone()
        return dict(zip(
            ['id', 'exam', 'topic', 'question', 'answer', 'solution', 'difficulty'],
            problem
        )) if problem else None

async def update_progress(user_id: int, topic: str):
    column = 'algebra_solved' if topic == 'Алгебра' else 'geometry_solved'
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(f'''
            INSERT INTO users (user_id, {column}) 
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET {column} = {column} + 1
        ''', (user_id,))
        await conn.commit()

async def get_solved_count(user_id: int, topic: str) -> int:
    column = 'algebra_solved' if topic == 'Алгебра' else 'geometry_solved'
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            f'SELECT {column} FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0