from utils.database import add_bulk_problems
import random
from fractions import Fraction
topics = {
    "Алгебра": [
        {
            "text": r"Решите уравнение: \( x^2 - {a}x + {b} = 0 \).",
            "answer": "{x1};{x2}",
            "hint": r"Используйте формулу дискриминанта: D = {a}² - 4·{b}."
        }
    ],
    "Геометрия": [
        {
            "text": r"Найдите площадь круга с радиусом {r} см.",
            "answer": "{area}",
            "hint": r"Формула площади круга: \( S = \pi r^2 \)."
        }
    ],
    "Теория вероятностей": [
        {
            "text": r"Вероятность события A равна {p}. Найдите вероятность противоположного события.",
            "answer": "{answer}",
            "hint": r"Вероятность противоположного события: \( P(\overline{A}) = 1 - P(A) \)."
        }
    ],
    "Статистика": [
        {
            "text": r"Дан набор данных: {data}. Найдите среднее арифметическое.",
            "answer": "{mean}",
            "hint": r"Среднее = (сумма всех элементов) / (количество элементов)."
        }
    ]
}

def generate_problems():
    problems = []
    for _ in range(100):
        topic = random.choice(list(topics.keys()))
        template = random.choice(topics[topic])
        exam_type = random.choice(["ЕГЭ", "ОГЭ"])
        level = "база" if exam_type == "ОГЭ" else random.choice(["база", "профиль"])
        complexity = random.randint(3, 5) if exam_type == "ЕГЭ" else random.randint(1, 2)
        if topic == "Алгебра":
            while True:
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                # Для уравнения x² - ax + b = 0
                # Дискриминант: D = a² - 4b
                discriminant = a * a - 4 * b

                if discriminant >= 0:
                    sqrt_d = discriminant ** 0.5
                    # Корни: x = (a ± √D) / 2
                    x1 = (a + sqrt_d) / 2
                    x2 = (a - sqrt_d) / 2

                    # Проверка корней (подстановка в исходное уравнение)
                    check1 = abs(x1 * x1 - a * x1 + b) < 0.0001
                    check2 = abs(x2 * x2 - a * x2 + b) < 0.0001

                    if check1 and check2:
                        # Сортировка корней (меньший первым)
                        x1, x2 = sorted([x1, x2])

                        # Округление и форматирование
                        x1 = round(x1, 2) if not x1.is_integer() else int(x1)
                        x2 = round(x2, 2) if not x2.is_integer() else int(x2)

                        # Форматирование ответа
                        if x1 == x2:
                            answer = str(x1)
                        else:
                            answer = f"{x1}; {x2}"
                        break

            text = template["text"].format(a=a, b=b)
            hint = (f"Решение квадратного уравнения x² - {a}x + {b} = 0:\n"
                   f"D = {a}² - 4·{b} = {discriminant}\n"
                   f"x₁ = ({a} + √{discriminant}) / 2 = {x1}\n"
                   f"x₂ = ({a} - √{discriminant}) / 2 = {x2}")
        elif topic == "Геометрия":
            r = random.randint(1, 10)
            area = round(3.14 * r ** 2, 2)
            text = template["text"].format(r=r)
            answer = str(area)
            hint = template["hint"]
        elif topic == "Теория вероятностей":
            p = Fraction(random.randint(1, 9), 10)
            fraction_answer = 1 - p
            decimal_answer = float(fraction_answer)
            answer = f"{fraction_answer}"
            if fraction_answer.denominator != 1:
                answer += f"; {decimal_answer:.2f}"
            text = template["text"].format(p=float(p))
            hint = (template["hint"] +
                   f"\nРешение: 1 - {p} = {fraction_answer}" +
                   "\nОтвет можно записать обыкновенной дробью (например, 3/10) " +
                   "или десятичной дробью.")
        elif topic == "Статистика":
            data = [random.randint(1, 20) for _ in range(5)]
            mean = sum(data) / len(data)

            if mean.is_integer():
                answer = str(int(mean))
            else:
                decimal_mean = round(mean, 2)
                fraction_mean = Fraction(mean).limit_denominator(100)
                if float(fraction_mean) == decimal_mean:
                    answer = f"{decimal_mean}; {fraction_mean}"
                else:
                    answer = str(decimal_mean)

            text = template["text"].format(data=", ".join(map(str, data)))
            hint = (template["hint"] +
                   f"\nРешение: ({' + '.join(map(str, data))}) ÷ {len(data)} = {answer.split(';')[0]}")

            if ";" in answer:
                hint += "\nОтвет можно ввести как десятичной дробью, так и обыкновенной."
        if isinstance(answer, str):
            if ("." in answer and len(answer.split(".")[1]) > 2) or "/" in answer:
                hint += "\n\nℹ️ *Совет:* Можно ввести дробь (1/3) или округлить до двух знаков."
        else:
            answer = str(answer)
        problem = {
            "topic": topic,
            "text": text,
            "answer": answer,
            "exam_type": exam_type,
            "level": level,
            "complexity": complexity,
            "hint": hint
        }
        problems.append(problem)

    add_bulk_problems(problems)
    print(f"✅ Добавлено {len(problems)} задач!")

if __name__ == "__main__":
    generate_problems()