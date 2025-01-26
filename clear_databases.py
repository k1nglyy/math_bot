import os
from pathlib import Path

# Получаем путь к директории data
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def clear_databases():
    try:
        # Удаляем файл math_problems.db
        db_path = DATA_DIR / "math_problems.db"
        if db_path.exists():
            os.remove(db_path)
            print(f"✅ База данных {db_path} успешно удалена")

        # Удаляем файл problems.json, если он существует
        json_path = DATA_DIR / "problems.json"
        if json_path.exists():
            os.remove(json_path)
            print(f"✅ Файл {json_path} успешно удален")

        print("\n🔄 Базы данных очищены. Теперь вы можете заново заполнить их с помощью:")
        print("1. python generate_problems.py")

    except Exception as e:
        print(f"❌ Ошибка при очистке баз данных: {e}")


if __name__ == "__main__":
    confirm = input("⚠️ Вы уверены, что хотите очистить все базы данных? (y/n): ")
    if confirm.lower() == 'y':
        clear_databases()
    else:
        print("❌ Операция отменена")