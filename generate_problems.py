from utils.database import add_bulk_problems
import random
from fractions import Fraction
topics = {
    "Алгебра": [
        {
            "text": r"Решите уравнение: \( x^2 - {a}x + {b} = 0 \).",
            "answer": "{x1};{x2}",
            "hint": r"Используйте теорему Виета: \( x_1 + x_2 = {a}, \, x_1 \cdot x_2 = {b} \)."
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
                a = random.randint(1, 5)
                b = random.randint(-10, 10)
                c = random.randint(-10, 10)
                discriminant = b ** 2 - 4 * a * c
                if discriminant >= 0:
                    sqrt_d = discriminant ** 0.5
                    x1 = (-b + sqrt_d) / (2 * a)
                    x2 = (-b - sqrt_d) / (2 * a)
                    x1 = round(x1, 2) if not x1.is_integer() else int(x1)
                    x2 = round(x2, 2) if not x2.is_integer() else int(x2)
                    roots = sorted([x1, x2], reverse=True)
                    answer = f"{roots[0]}; {roots[1]}" if x1 != x2 else f"{x1}"
                    break
            equation = f"{a}x² {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)} = 0"
            text = f"Решите уравнение: {equation}"
            hint = (
                f"Формула дискриминанта: D = b² - 4ac = {b}² - 4*{a}*{c} = {discriminant}.\n"
                f"Корни: x = (−b ± √D)/(2a) = (−({b}) ± {sqrt_d:.2f})/(2*{a})"
            )
        elif topic == "Геометрия":
            r = random.randint(1, 10)
            area = round(3.14 * r ** 2, 2)
            text = template["text"].format(r=r)
            answer = str(area)
            hint = template["hint"]
        elif topic == "Теория вероятностей":
            p = round(random.uniform(0.1, 0.9), 2)
            decimal_answer = round(1 - p, 2)
            fraction_answer = Fraction(decimal_answer).limit_denominator(10)
            answer = f"{decimal_answer:.2f}; {fraction_answer}"
            text = template["text"].format(p=p)
            hint = template["hint"] + "\nМожно ввести ответ как десятичной дробью (0.33), так и обыкновенной (1/3)."
        elif topic == "Статистика":
            data = [random.randint(1, 10) for _ in range(5)]
            mean = sum(data) / len(data)
            decimal_mean = round(mean, 2)
            fraction_mean = Fraction(mean).limit_denominator(10)
            answer = f"{decimal_mean:.2f}; {fraction_mean}"
            text = template["text"].format(data=", ".join(map(str, data)))
            hint = template["hint"] + "\nОтвет можно ввести десятичным (3.5) или дробью (7/2)."
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