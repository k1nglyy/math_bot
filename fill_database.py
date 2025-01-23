import asyncio
from utils.database import init_db
import aiosqlite

async def async_fill_database():
    await init_db()  # Асинхронная инициализация

    async with aiosqlite.connect('data/problems.db') as conn:
        cursor = await conn.cursor()
        tasks = [
            ('algebra', 'Решите уравнение: 3x + 5 = 20', '5'),
            ('geometry', 'Найдите площадь круга с радиусом 5 см', '78.54'),
        ]
        await cursor.executemany(
            'INSERT INTO problems (topic, question, answer) VALUES (?, ?, ?)',
            tasks
        )
        await conn.commit()
    print("✅ База данных успешно заполнена!")


if __name__ == "__main__":
    asyncio.run(async_fill_database())