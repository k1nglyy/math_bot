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
                logger.debug(f"Loaded {sum(len(v) for k, v in data.items())} problems")
                return data
        except Exception as e:
            logger.error(f"Error loading problems: {str(e)}")
            return {"ОГЭ": {}, "ЕГЭ": {}}

    def get_problem(self, exam: str, topic: str, difficulty: int) -> Optional[Dict]:
        try:
            exam_problems = self.problems.get(exam, {})
            topic_problems = exam_problems.get(topic, [])
            filtered = [p for p in topic_problems if p.get("difficulty") == difficulty]
            if filtered:
                problem = random.choice(filtered)
                logger.debug(f"Found problem: {problem['question']}")
                return problem
            logger.warning(f"No problems found for {exam}/{topic} difficulty {difficulty}")
            return self._generate_fallback(topic, difficulty)

        except Exception as e:
            logger.error(f"Error getting problem: {str(e)}")
            return self._generate_fallback(topic, difficulty)

    def _generate_fallback(self, topic: str, difficulty: int) -> Dict:
        try:
            logger.info("Generating fallback problem")
            if topic == "Алгебра":
                a = random.randint(1, 3 * difficulty)
                b = random.randint(1, 5 * difficulty)
                return {
                    "question": f"Решите уравнение: {a}x + {b} = 0",
                    "answer": str(round(-b / a, 2)),
                    "solution": f"**Решение:**\n{a}x = {-b}\nx = {-b}/{a}\nx = {round(-b / a, 2)}",
                    "difficulty": difficulty
                }
            else:
                a = random.randint(1, 2 * difficulty)
                b = random.randint(1, 3 * difficulty)
                return {
                    "question": f"Найдите площадь прямоугольника со сторонами {a} и {b}",
                    "answer": str(a * b),
                    "solution": f"**Решение:**\nПлощадь = {a} × {b} = {a * b}",
                    "difficulty": difficulty
                }
        except Exception as e:
            logger.error(f"Fallback generation failed: {str(e)}")
            return {
                "question": "Решите уравнение: 2x + 4 = 0",
                "answer": "-2",
                "solution": "**Решение:**\n2x = -4\nx = -2",
                "difficulty": 1
            }