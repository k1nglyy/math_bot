# utils/problem_bank.py

import json
import random
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROBLEMS_PATH = BASE_DIR / "data" / "problems.json"


class ProblemBank:
    def __init__(self):
        self.problems = self._load_problems()
        logger.info("Problem bank initialized")

    def _load_problems(self) -> dict:
        try:
            with open(PROBLEMS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug(f"Loaded {len(data)} problems")
                return data
        except Exception as e:
            logger.error(f"Error loading problems: {str(e)}")
            return []

    def get_random_problem(self, exam_type: str, level: str) -> Optional[Dict]:
        """Получает случайную задачу с учетом типа экзамена и уровня"""
        try:
            suitable_problems = [
                problem for problem in self.problems
                if problem["exam_type"] == exam_type and problem["level"] == level
            ]

            if suitable_problems:
                problem = random.choice(suitable_problems)
                logger.info(f"Selected problem: {problem['text'][:50]}...")
                return {
                    "topic": problem["topic"],
                    "text": problem["text"],
                    "answer": problem["answer"],
                    "hint": problem["hint"],
                    "exam_type": problem["exam_type"],
                    "level": problem["level"],
                    "complexity": problem["complexity"]
                }
            else:
                logger.warning(f"No problems found for {exam_type} {level}")
                return None

        except Exception as e:
            logger.error(f"Error getting random problem: {e}")
            return None

    def _generate_fallback(self, topic: str, difficulty: int) -> Dict:
        """Генерирует простую задачу в случае ошибки"""
        try:
            logger.info("Generating fallback problem")
            if topic == "Алгебра":
                a = random.randint(1, 3 * difficulty)
                b = random.randint(1, 5 * difficulty)
                return {
                    "topic": "Алгебра",
                    "text": f"Решите уравнение: {a}x + {b} = 0",
                    "answer": str(round(-b / a, 2)),
                    "hint": f"Решение:\n{a}x = {-b}\nx = {-b}/{a}\nx = {round(-b / a, 2)}",
                    "exam_type": "ЕГЭ",
                    "level": "база",
                    "complexity": difficulty
                }
            else:
                a = random.randint(1, 2 * difficulty)
                b = random.randint(1, 3 * difficulty)
                return {
                    "topic": "Геометрия",
                    "text": f"Найдите площадь прямоугольника со сторонами {a} и {b}",
                    "answer": str(a * b),
                    "hint": f"Решение:\nПлощадь = {a} × {b} = {a * b}",
                    "exam_type": "ЕГЭ",
                    "level": "база",
                    "complexity": difficulty
                }
        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            return {
                "topic": "Алгебра",
                "text": "Решите уравнение: 2x + 4 = 0",
                "answer": "-2",
                "hint": "Решение:\n2x = -4\nx = -2",
                "exam_type": "ЕГЭ",
                "level": "база",
                "complexity": 1
            }