from utils.database import add_bulk_problems
import random


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
            "text": r"В коробке {n} красных и {m} синих шаров. Какова вероятность вытащить красный шар?",
            "answer": "{prob}",
            "hint": r"Вероятность = число благоприятных исходов / общее число исходов."
        }
    ]
}


def generate_problems():
    problems = []
    for _ in range(100):
        topic = random.choice(list(topics.keys()))
        template = random.choice(topics[topic])
        if topic == "Алгебра":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            x1, x2 = random.sample(range(-5, 10), 2)
            text = template["text"].format(a=a, b=b)
            answer = template["answer"].format(x1=x1, x2=x2)
            hint = template["hint"].format(a=a, b=b)
        elif topic == "Геометрия":
            r = random.randint(1, 10)
            area = round(3.14 * r ** 2, 2)
            text = template["text"].format(r=r)
            answer = str(area)
            hint = template["hint"]
        elif topic == "Теория вероятностей":
            n = random.randint(1, 10)
            m = random.randint(1, 10)
            prob = round(n / (n + m), 2)
            text = template["text"].format(n=n, m=m)
            answer = str(prob)
            hint = template["hint"]

        problem = {
            "topic": topic,
            "text": text,
            "answer": answer,
            "exam_type": random.choice(["ЕГЭ", "ОГЭ"]),
            "level": random.choice(["база", "профиль"]),
            "complexity": random.randint(1, 5),
            "hint": hint
        }
        problems.append(problem)
    add_bulk_problems(problems)
    print(f"Добавлено {len(problems)} задач!")
if __name__ == "__main__":
    generate_problems()