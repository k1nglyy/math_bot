from utils.database import add_bulk_problems, init_db
import random
from fractions import Fraction
import math
import logging

logger = logging.getLogger(__name__)

def generate_geometry_problem(exam_type: str, level: str) -> dict:
    """Генерирует задачу по геометрии"""
    problems = [
        {
            "topic": "Геометрия",
            "text": """📐 *Задача на прямоугольный треугольник*

В прямоугольном треугольнике ABC:
• ∠C = 90°
• AC = 4
• BC = 3

Найдите sin(A).""",
            "answer": "0.6",
            "answer_type": "float",
            "exam_type": exam_type,
            "level": level,
            "complexity": 2,
            "hint": "sin(A) = противолежащий катет / гипотенуза = BC/AB",
            "solution": """1) По теореме Пифагора найдем AB:
AB² = AC² + BC² = 16 + 9 = 25
AB = 5
2) sin(A) = BC/AB = 3/5 = 0.6"""
        },
        {
            "topic": "Геометрия",
            "text": """📐 *Задача на площадь треугольника*

В треугольнике ABC:
• AB = 6
• Высота к стороне AB равна 4

Найдите площадь треугольника.""",
            "answer": "12",
            "answer_type": "integer",
            "exam_type": exam_type,
            "level": level,
            "complexity": 1,
            "hint": "S = ½ * основание * высота",
            "solution": "S = ½ * 6 * 4 = 12"
        }
    ]
    return random.choice(problems)

def generate_trigonometry_problem(exam_type: str, level: str) -> dict:
    """Генерирует задачу по тригонометрии"""
    angles = {
        0: {"sin": "0", "cos": "1"},
        30: {"sin": "1/2", "cos": "√3/2"},
        45: {"sin": "√2/2", "cos": "√2/2"},
        60: {"sin": "√3/2", "cos": "1/2"},
        90: {"sin": "1", "cos": "0"}
    }
    
    angle = random.choice(list(angles.keys()))
    func = random.choice(['sin', 'cos'])
    answer = angles[angle][func]

    return {
        "topic": "Тригонометрия",
        "text": f"🔄 Вычислите {func}({angle}°)",
        "answer": answer,
        "answer_type": "trig",
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": f"Вспомните табличное значение {func}({angle}°)",
        "solution": f"Табличное значение: {func}({angle}°) = {answer}"
    }

def generate_logarithm_problem(exam_type: str, level: str) -> dict:
    """Генерирует задачу на логарифмы"""
    base = random.choice([2, 3, 5, 10])
    power = random.randint(1, 4)
    number = base ** power

    return {
        "topic": "Логарифмы",
        "text": f"📉 Вычислите log_{base}({number})",
        "answer": str(power),
        "answer_type": "integer",
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": f"По определению: log_a(b) = x, если a^x = b",
        "solution": f"{base}^{power} = {number}, поэтому log_{base}({number}) = {power}"
    }

def generate_exponential_problem(exam_type: str, level: str) -> dict:
    """Генерирует показательную задачу"""
    base = random.choice([2, 3, 5])
    power = random.randint(-2, 3)
    result = base ** power

    return {
        "topic": "Показательные уравнения",
        "text": f"📈 Вычислите {base}^{power}",
        "answer": str(result),
        "answer_type": "integer",
        "exam_type": exam_type,
        "level": level,
        "complexity": 2,
        "hint": f"Используйте правила возведения в степень",
        "solution": f"{base}^{power} = {result}"
    }

def generate_problems():
    """Генерирует все задачи и добавляет их в базу данных"""
    try:
        init_db()
        problems = []
        
        exam_levels = [
            ("ЕГЭ", "профиль"),
            ("ЕГЭ", "база"),
            ("ОГЭ", "база")
        ]
        
        generators = [
            generate_geometry_problem,
            generate_trigonometry_problem,
            generate_logarithm_problem,
            generate_exponential_problem
        ]
        
        # Генерируем 10 задач каждого типа для каждого уровня
        for exam_type, level in exam_levels:
            for generator in generators:
                for _ in range(10):
                    problem = generator(exam_type, level)
                    problems.append(problem)
        
        # Добавляем задачи в базу данных
        add_bulk_problems(problems)
        
        logger.info(f"Generated {len(problems)} problems")
        print(f"\nСгенерировано задач:")
        for exam_type, level in exam_levels:
            count = sum(1 for p in problems if p['exam_type'] == exam_type and p['level'] == level)
            print(f"- {exam_type} ({level}): {count} задач")
            
    except Exception as e:
        logger.error(f"Error generating problems: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    generate_problems()