import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import Config, load_config
from handlers import user_handlers
from utils.database import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка конфига
config: Config = load_config()

# Инициализация бота и диспетчера
async def main():
    try:
        # Инициализируем базу данных
        init_db()
        logger.info("Database initialized")
        
        # Создаем объекты бота и диспетчера с хранилищем состояний
        bot = Bot(token=config.tg_bot.token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрируем роутеры
        dp.include_router(user_handlers.router)
        
        # Удаляем все обновления, накопившиеся за время отключения бота
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Starting bot")
        
        # Запускаем поллинг
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")