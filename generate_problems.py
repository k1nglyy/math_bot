from utils.database import add_bulk_problems, init_db
import random
from fractions import Fraction
import math


def generate_nice_quadratic(exam_type: str, level: str) -> dict:
    """Генерирует квадратное уравнение с 'красивыми' корнями"""
    x1 = random.randint(-6, 6)
    x2 = random.randint(-6, 6)

    a = 1
    b = -(x1 + x2)
    c = x1 * x2

    if x1 == 0 and x2 == 0:
        return generate_nice_quadratic(exam_type, level)

    equation = "x²"
    if b != 0:
        sign = " + " if b > 0 else " - "
        b_abs = abs(b)
        equation += f"{sign}{b_abs}x"
    if c != 0:
        sign = " + " if c > 0 else " - "
        c_abs = abs(c)
        equation += f"{sign}{c_abs}"
    equation += " = 0"

    if x1 == x2:
        answer = str(x1)
    else:
        answer = f"{min(x1, x2)};{max(x1, x2)}"

    hint = (
        f"1) Найдите дискриминант: D = b² - 4ac\n"
        f"   D = ({b})² - 4·({a})·({c}) = {b * b - 4 * a * c}\n"
        f"2) Используйте формулу: x = (-b ± √D) / (2a)\n"
        f"3) x = ({-b} ± √{b * b - 4 * a * c}) / (2·{a})\n"
        f"4) x₁ = {x1}, x₂ = {x2}"
    )

    return {
        "topic": "Алгебра",
        "text": f"Решите квадратное уравнение: {equation}",
        "answer": answer,
        "exam_type": exam_type,
        "level": level,
        "complexity": random.randint(1, 3),
        "hint": hint
    }


def generate_circle_problem(exam_type: str, level: str) -> dict:
    """Генерирует задачу на площадь круга с π = 3.14"""
    r = random.randint(1, 10)
    # Используем π = 3.14 и округляем до 2 знаков после запятой
    area = round(3.14 * r * r, 2)

    return {
        "topic": "Геометрия",
        "text": (
            f"Найдите площадь круга с радиусом {r} см.\n"
            "Число π округлите до 3.14"
        ),
        "answer": str(area),
        "exam_type": exam_type,
        "level": level,
        "complexity": random.randint(1, 3),
        "hint": (
            f"1) Используйте формулу площади круга: S = πr²\n"
            f"2) Подставьте значения: S = 3.14 · {r}²\n"
            f"3) S = 3.14 · {r * r} = {area} см²"
        )
    }


def generate_probability_problem(exam_type: str, level: str) -> dict:
    """Генерирует задачу по теории вероятностей"""
    numerator = random.randint(1, 5)
    denominator = random.randint(6, 10)
    probability = round(numerator / denominator, 2)

    return {
        "topic": "Теория вероятностей",
        "text": f"Вероятность события A равна {probability}. Найдите вероятность противоположного события.",
        "answer": str(round(1 - probability, 2)),
        "exam_type": exam_type,
        "level": level,
        "complexity": random.randint(1, 3),
        "hint": "Вероятность противоположного события = 1 - P(A)"
    }


def generate_statistics_problem(exam_type: str, level: str) -> dict:
    """Генерирует задачу по статистике с одним знаком после запятой в ответе"""

    # Генерируем базовое среднее значение с одним знаком после запятой
    mean = round(random.randint(20, 90) / 10, 1)  # получим числа вида 2.5, 3.4, и т.д.
    count = 5  # количество чисел

    # Генерируем набор чисел, дающих нужное среднее
    numbers = []
    sum_needed = mean * count

    # Генерируем первые count-1 чисел
    for i in range(count - 1):
        if i == 0:
            # Первое число делаем немного отличающимся от среднего
            num = round(mean + random.choice([-1.5, -1, 1, 1.5]), 1)
        else:
            # Остальные числа генерируем в пределах ±2 от среднего
            num = round(mean + random.uniform(-2, 2), 1)
        numbers.append(num)

    # Вычисляем последнее число, чтобы получить нужное среднее
    last_number = round(sum_needed - sum(numbers), 1)

    # Если последнее число слишком отличается от остальных, генерируем заново
    if abs(last_number - mean) > 3:
        return generate_statistics_problem(exam_type, level)

    numbers.append(last_number)
    random.shuffle(numbers)  # перемешиваем числа

    # Проверяем, что среднее действительно получилось правильным
    actual_mean = round(sum(numbers) / len(numbers), 1)
    if actual_mean != mean:
        return generate_statistics_problem(exam_type, level)

    # Формируем текст задачи с разными формулировками
    task_variants = [
        f"В таблице приведены результаты измерений: {', '.join(map(str, numbers))}.\nНайдите среднее арифметическое этих чисел.",
        f"Спортсмен пробежал {count} кругов по стадиону. Время каждого круга (в минутах): {', '.join(map(str, numbers))}.\nНайдите среднее время одного круга.",
        f"Ученик получил {count} оценок: {', '.join(map(str, numbers))}.\nКакой средний балл получился у ученика?",
        f"Датчик температуры делал замеры каждый час: {', '.join(map(str, numbers))}.\nОпределите среднюю температуру за период наблюдений."
    ]

    task_text = random.choice(task_variants)

    return {
        "topic": "Статистика",
        "text": task_text,
        "answer": str(mean),
        "exam_type": exam_type,
        "level": level,
        "complexity": random.randint(1, 3),
        "hint": (
            f"1) Сложите все числа:\n"
            f"   {' + '.join(map(str, numbers))} = {sum(numbers)}\n"
            f"2) Разделите сумму на количество чисел:\n"
            f"   {sum(numbers)} ÷ {count} = {mean}"
        )
    }


def generate_problems():
    # Инициализируем базу данных
    init_db()
    problems = []

    TASKS_PER_CATEGORY = 20  # Устанавливаем одинаковое количество задач для каждой категории

    # Генерация задач для каждого типа экзамена и уровня
    for exam_type in ["ЕГЭ", "ОГЭ"]:
        levels = ["база", "профиль"] if exam_type == "ЕГЭ" else ["база"]
        for level in levels:
            # Квадратные уравнения
            for _ in range(TASKS_PER_CATEGORY):
                problem = generate_nice_quadratic(exam_type, level)
                problems.append(problem)

            # Задачи по геометрии
            for _ in range(TASKS_PER_CATEGORY):
                problem = generate_circle_problem(exam_type, level)
                problems.append(problem)

            # Задачи по теории вероятностей
            for _ in range(TASKS_PER_CATEGORY):
                problem = generate_probability_problem(exam_type, level)
                problems.append(problem)

            # Задачи по статистике
            for _ in range(TASKS_PER_CATEGORY):
                problem = generate_statistics_problem(exam_type, level)
                problems.append(problem)

    # Добавляем все задачи в базу данных
    add_bulk_problems(problems)
    print(f"✅ Добавлено {len(problems)} задач в базу данных!")
    print("\nРаспределение задач:")
    topics = {}
    for p in problems:
        topic = p['topic']
        exam = p['exam_type']
        level = p['level']
        key = f"{topic} ({exam}, {level})"
        topics[key] = topics.get(key, 0) + 1

    for topic, count in sorted(topics.items()):
        print(f"- {topic}: {count} задач")


if __name__ == "__main__":
    generate_problems()