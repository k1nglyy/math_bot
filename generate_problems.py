from utils.database import add_bulk_problems, init_db
import random
from fractions import Fraction
import math


def generate_problems():
    # Инициализируем базу данных
    init_db()

    problems = []

    # Генерация задач по алгебре
    for exam_type in ["ЕГЭ", "ОГЭ"]:
        for level in ["база", "профиль"] if exam_type == "ЕГЭ" else ["база"]:
            for _ in range(20):  # 20 задач каждого типа
                # Квадратное уравнение
                a = random.randint(-5, 5)
                while a == 0:  # избегаем a = 0
                    a = random.randint(-5, 5)
                b = random.randint(-10, 10)
                c = random.randint(-10, 10)

                # Вычисляем корни
                D = b ** 2 - 4 * a * c
                if D >= 0:
                    x1 = (-b + math.sqrt(D)) / (2 * a)
                    x2 = (-b - math.sqrt(D)) / (2 * a)
                    x1 = round(x1, 2)
                    x2 = round(x2, 2)
                    answer = f"{min(x1, x2)};{max(x1, x2)}" if x1 != x2 else str(x1)

                    problem = {
                        "topic": "Алгебра",
                        "text": f"Решите квадратное уравнение: {a}x² + {b}x + {c} = 0",
                        "answer": answer,
                        "exam_type": exam_type,
                        "level": level,
                        "complexity": random.randint(1, 3),
                        "hint": f"Используйте дискриминант: D = {b}² - 4·{a}·{c}"
                    }
                    problems.append(problem)

    # Генерация задач по геометрии
    for exam_type in ["ЕГЭ", "ОГЭ"]:
        for level in ["база", "профиль"] if exam_type == "ЕГЭ" else ["база"]:
            for _ in range(20):
                r = random.randint(1, 10)
                area = round(math.pi * r ** 2, 2)

                problem = {
                    "topic": "Геометрия",
                    "text": f"Найдите площадь круга с радиусом {r} см.",
                    "answer": str(area),
                    "exam_type": exam_type,
                    "level": level,
                    "complexity": random.randint(1, 3),
                    "hint": f"Используйте формулу площади круга: S = πr². При r = {r}"
                }
                problems.append(problem)

    # Генерация задач по теории вероятностей
    for exam_type in ["ЕГЭ", "ОГЭ"]:
        for level in ["база", "профиль"] if exam_type == "ЕГЭ" else ["база"]:
            for _ in range(20):
                numerator = random.randint(1, 5)
                denominator = random.randint(6, 10)
                probability = round(numerator / denominator, 2)

                problem = {
                    "topic": "Теория вероятностей",
                    "text": f"Вероятность события A равна {probability}. Найдите вероятность противоположного события.",
                    "answer": str(round(1 - probability, 2)),
                    "exam_type": exam_type,
                    "level": level,
                    "complexity": random.randint(1, 3),
                    "hint": "Вероятность противоположного события = 1 - P(A)"
                }
                problems.append(problem)

    # Генерация задач по статистике
    for exam_type in ["ЕГЭ", "ОГЭ"]:
        for level in ["база", "профиль"] if exam_type == "ЕГЭ" else ["база"]:
            for _ in range(20):
                # Генерируем набор чисел
                data = [random.randint(1, 20) for _ in range(5)]
                mean = sum(data) / len(data)

                problem = {
                    "topic": "Статистика",
                    "text": f"Найдите среднее арифметическое чисел: {', '.join(map(str, data))}",
                    "answer": str(round(mean, 2)),
                    "exam_type": exam_type,
                    "level": level,
                    "complexity": random.randint(1, 3),
                    "hint": f"Среднее арифметическое = ({' + '.join(map(str, data))}) ÷ {len(data)}"
                }
                problems.append(problem)

    # Добавляем все задачи в базу данных
    add_bulk_problems(problems)
    print(f"✅ Добавлено {len(problems)} задач в базу данных!")


if __name__ == "__main__":
    generate_problems()