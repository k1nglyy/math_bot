import aiosqlite
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "problems.db"

async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    exam TEXT DEFAULT 'ОГЭ',
                    algebra_solved INTEGER DEFAULT 0,
                    geometry_solved INTEGER DEFAULT 0,
                    difficulty INTEGER DEFAULT 1
                )
            ''')
            await conn.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

async def save_user_exam(user_id: int, exam: str):
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                '''INSERT OR REPLACE INTO users 
                (user_id, exam) 
                VALUES (?, ?)''',
                (user_id, exam)
            )
            await conn.commit()
    except Exception as e:
        logger.error(f"Error saving exam: {str(e)}")
        raise

async def get_user_difficulty(user_id: int) -> int:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,)
            )
            cursor = await conn.execute(
                "SELECT difficulty FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 1
    except Exception as e:
        logger.error(f"Error getting difficulty: {str(e)}")
        return 1

async def update_user_stats(user_id: int, topic: str):
    try:
        column = "algebra_solved" if topic == "Алгебра" else "geometry_solved"
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                f'''UPDATE users 
                SET {column} = {column} + 1,
                    difficulty = difficulty + CASE
                        WHEN ({column} + 1) % 5 = 0 THEN 1
                        ELSE 0
                    END
                WHERE user_id = ?''',
                (user_id,)
            )
            await conn.commit()
    except Exception as e:
        logger.error(f"Error updating stats: {str(e)}")
        raise

async def get_user_stats(user_id: int) -> dict:
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.execute(
                '''SELECT exam, algebra_solved, 
                   geometry_solved, difficulty 
                   FROM users WHERE user_id = ?''',
                (user_id,)
            )
            result = await cursor.fetchone()
            return {
                'exam': result[0],
                'algebra': result[1],
                'geometry': result[2],
                'difficulty': result[3]
            } if result else {}
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {}