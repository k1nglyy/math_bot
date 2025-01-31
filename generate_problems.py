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


def generate_linear_equation(exam_type: str, level: str) -> dict:
    x = random.randint(-10, 10)
    a = random.randint(2, 5)
    b = a * x

    equation = f"{a}x = {b}"

    hint = (
        f"1) Перенесите все в одну сторону: {a}x - {b} = 0\n"
        f"2) Разделите обе части на {a}\n"
        f"3) x = {x}"
    )

    return {
        "topic": "Алгебра",
        "text": f"Решите линейное уравнение: {equation}",
        "answer": str(x),
        "exam_type": exam_type,
        "level": level,
        "complexity": 1,
        "hint": hint
    }


def generate_progression_problem(exam_type: str, level: str) -> dict:
    start = random.randint(1, 10)
    diff = random.randint(2, 5)
    length = 5

    sequence = [start + i * diff for i in range(length)]
    missing_idx = random.randint(1, length - 2)
    answer = sequence[missing_idx]
    sequence[missing_idx] = "..."

    return {
        "topic": "Алгебра",
        "text": (
            "В арифметической прогрессии пропущено число:\n"
            f"{', '.join(map(str, sequence))}\n"
            "Найдите это число."
        ),
        "answer": str(answer),
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": f"Разность прогрессии равна {diff}"
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


def generate_triangle_problem(exam_type: str, level: str) -> dict:
    a = random.randint(3, 10)
    h = random.randint(2, 8)
    area = round(0.5 * a * h, 1)

    return {
        "topic": "Геометрия",
        "text": (
            f"В треугольнике основание равно {a} см, "
            f"а высота, проведенная к этому основанию, равна {h} см. "
            "Найдите площадь треугольника."
        ),
        "answer": str(area),
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": "S = ½ · a · h"
    }


def generate_rectangle_problem(exam_type: str, level: str) -> dict:
    a = random.randint(3, 10)
    b = random.randint(3, 10)
    perimeter = 2 * (a + b)

    return {
        "topic": "Геометрия",
        "text": (
            f"Длина прямоугольника {a} см, ширина {b} см. "
            "Найдите периметр прямоугольника."
        ),
        "answer": str(perimeter),
        "exam_type": exam_type,
        "level": level,
        "complexity": 1,
        "hint": "P = 2(a + b)"
    }


def generate_probability_simple(exam_type: str, level: str) -> dict:
    total = random.randint(4, 10)
    favorable = random.randint(1, total - 1)
    probability = round(favorable / total, 2)

    variants = [
        f"В урне {total} шаров, из них {favorable} красных. Найдите вероятность достать красный шар.",
        f"В группе {total} студентов, из них {favorable} отличников. Какова вероятность случайно выбрать отличника?",
        f"Из {total} карточек с цифрами {favorable} четных. Найдите вероятность вытащить четную цифру."
    ]

    return {
        "topic": "Теория вероятностей",
        "text": random.choice(variants),
        "answer": str(probability),
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": f"Вероятность = {favorable}/{total}"
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
        f"Датчик температуры делал замеры каждый час: {', '.join(map(str, numbers))}.\nОпределите среднюю температуру за период наблюдений."
    ]
    
    # Отдельно генерируем вариант с оценками
    if random.random() < 0.25:  # 25% шанс получить задачу с оценками
        # Генерируем оценки от 2 до 5
        grade_numbers = [random.randint(2, 5) for _ in range(count)]
        grade_mean = round(sum(grade_numbers) / len(grade_numbers), 1)
        task_text = f"Ученик получил {count} оценок: {', '.join(map(str, grade_numbers))}.\nКакой средний балл получился у ученика?"
        numbers = grade_numbers
        mean = grade_mean
    else:
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


def generate_basic_exponential(exam_type: str, level: str) -> dict:
    """Генерирует простое показательное уравнение вида a^x = b"""
    base = random.randint(2, 5)
    power = random.randint(1, 4)
    result = base ** power

    equation = f"{base}^x = {result}"

    hint = (
        f"1) Используйте определение логарифма\n"
        f"2) x = log_{base}({result})\n"
        f"3) Так как {base}^{power} = {result}\n"
        f"4) x = {power}"
    )

    return {
        "topic": "Показательные уравнения",
        "text": f"Решите уравнение: {equation}",
        "answer": str(power),
        "answer_type": "integer",  # тип ответа - целое число
        "exam_type": exam_type,
        "level": level,
        "complexity": 1,
        "hint": hint
    }


def generate_basic_logarithm(exam_type: str, level: str) -> dict:
    """Генерирует задание на вычисление логарифма"""
    base = random.randint(2, 5)
    power = random.randint(1, 4)
    number = base ** power

    question = f"log_{base}({number})"

    hint = (
        f"1) По определению логарифма: log_a(b) = c, если a^c = b\n"
        f"2) В нашем случае: {base}^{power} = {number}\n"
        f"3) Значит, log_{base}({number}) = {power}"
    )

    return {
        "topic": "Логарифмы",
        "text": f"Вычислите: {question}",
        "answer": str(power),
        "answer_type": "integer",  # тип ответа - целое число
        "exam_type": exam_type,
        "level": level,
        "complexity": 1,
        "hint": hint
    }


def generate_basic_trig(exam_type: str, level: str) -> dict:
    """Генерирует простые тригонометрические задания"""
    angles = {
        0: {"sin": "0", "cos": "1"},
        30: {"sin": "1/2", "cos": "√3/2"},
        45: {"sin": "√2/2", "cos": "√2/2"},
        60: {"sin": "√3/2", "cos": "1/2"},
        90: {"sin": "1", "cos": "0"}
    }
    
    angle = random.choice(list(angles.keys()))
    func = random.choice(['sin', 'cos'])
    answer = angles[angle][func]  # теперь храним один ответ

    return {
        "topic": "Тригонометрия",
        "text": f"Вычислите {func}({angle}°)",
        "answer": answer,  # один ответ вместо списка
        "answer_type": "trig",  # изменен тип ответа
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": f"Табличное значение: {func}({angle}°) = {answer}"
    }


def generate_problems():
    init_db()
    problems = []
    
    TASKS_PER_CATEGORY = 20

    for exam_type in ["ЕГЭ", "ОГЭ"]:
        levels = ["база", "профиль"] if exam_type == "ЕГЭ" else ["база"]
        for level in levels:
            if exam_type == "ЕГЭ":
                # Добавляем новые типы заданий для ЕГЭ
                for _ in range(TASKS_PER_CATEGORY):
                    problems.append(generate_basic_exponential(exam_type, level))
                    problems.append(generate_basic_logarithm(exam_type, level))
                    problems.append(generate_basic_trig(exam_type, level))
            
            # Базовые задания теперь только для ОГЭ
            if exam_type == "ОГЭ":
                for _ in range(TASKS_PER_CATEGORY // 3):
                    problems.append(generate_nice_quadratic(exam_type, level))
                    problems.append(generate_linear_equation(exam_type, level))
                    problems.append(generate_progression_problem(exam_type, level))
                    problems.append(generate_circle_problem(exam_type, level))
                    problems.append(generate_triangle_problem(exam_type, level))
                    problems.append(generate_rectangle_problem(exam_type, level))
                    problems.append(generate_probability_simple(exam_type, level))
                    problems.append(generate_statistics_problem(exam_type, level))

    # Добавляем проверку количества сгенерированных задач
    print(f"\nСгенерировано задач:")
    exam_counts = {}
    for p in problems:
        key = f"{p['exam_type']} ({p['level']})"
        exam_counts[key] = exam_counts.get(key, 0) + 1
    
    for exam, count in exam_counts.items():
        print(f"- {exam}: {count} задач")

    # Добавляем все задачи в базу данных
    add_bulk_problems(problems)
    print(f"\n✅ Добавлено {len(problems)} задач в базу данных!")


# Функция проверки ответа
def check_answer(problem: dict, user_answer: str) -> bool:
    """Проверяет ответ пользователя с учетом типа ответа"""
    answer_type = problem.get("answer_type", "string")
    
    if answer_type == "integer":
        try:
            return int(user_answer) == int(problem["answer"])
        except ValueError:
            return False
            
    elif answer_type == "float":
        try:
            return abs(float(user_answer) - float(problem["answer"])) < 0.001
        except ValueError:
            return False
            
    elif answer_type == "trig":
        # Нормализуем ответ пользователя
        user_answer = user_answer.replace(" ", "").lower()
        correct_answer = problem["answer"].replace(" ", "").lower()
        
        # Проверяем точное совпадение
        if user_answer == correct_answer:
            return True
            
        # Проверяем числовое значение, если возможно
        try:
            if "√" in correct_answer:
                # Преобразуем √2/2 в 0.707, √3/2 в 0.866 и т.д.
                if "√2/2" in correct_answer:
                    correct_value = 0.707
                elif "√3/2" in correct_answer:
                    correct_value = 0.866
                else:
                    return user_answer == correct_answer
                
                user_value = float(user_answer)
                return abs(user_value - correct_value) < 0.01
            
            # Для простых дробей (например, 1/2)
            if "/" in correct_answer:
                num, den = map(int, correct_answer.split("/"))
                correct_value = num / den
                user_value = float(user_answer)
                return abs(user_value - correct_value) < 0.01
                
        except (ValueError, ZeroDivisionError):
            pass
            
        return False
            
    # Для остальных типов - строгое строковое сравнение
    return user_answer.strip() == problem["answer"].strip()


if __name__ == "__main__":
    generate_problems()