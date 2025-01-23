import asyncio
import aiosqlite
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'problems.db'

async def fill_sample_data():
    (BASE_DIR / 'data').mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(fill_sample_data())