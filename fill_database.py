from utils.database import create_tables, add_sample_problems

if __name__ == "__main__":
    create_tables()
    add_sample_problems()
    print("✅ База данных заполнена!")