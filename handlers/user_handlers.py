from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.database import (
    get_problem,
    update_user_stats,
    get_user_stats,
    get_user_achievements,
    check_achievements,
    get_adaptive_problem
)
import logging
from datetime import datetime
from typing import List, Dict
import random
from generate_problems import (
    generate_basic_exponential,
    generate_basic_logarithm,
    generate_basic_trig
)
from keyboards.keyboards import main_menu, exam_menu, level_menu

router = Router()
logger = logging.getLogger(__name__)

# Обновляем категории и их иконки
TOPIC_ICONS = {
    "Алгебра": "📊",
    "Геометрия": "📐",
    "Теория вероятностей": "🎲",
    "Статистика": "📈",
    "Показательные уравнения": "📈",
    "Логарифмы": "📉",
    "Тригонометрия": "🔄"
}

# Обновляем главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Выбрать экзамен"), KeyboardButton(text="✨ Получить задачу")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="💡 Помощь")],
        [KeyboardButton(text="🏆 Достижения"), KeyboardButton(text="📚 Темы")]
    ],
    resize_keyboard=True
)

# Добавляем меню тем
topics_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Алгебра"), KeyboardButton(text="📐 Геометрия")],
        [KeyboardButton(text="📈 Показательные"), KeyboardButton(text="📉 Логарифмы")],
        [KeyboardButton(text="🔄 Тригонометрия"), KeyboardButton(text="🎲 Вероятности")],
        [KeyboardButton(text="🔙 Вернуться в меню")]
    ],
    resize_keyboard=True
)

exam_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 ЕГЭ"), KeyboardButton(text="📖 ОГЭ")],
        [KeyboardButton(text="🔙 Вернуться в меню")]
    ],
    resize_keyboard=True
)

level_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 База"), KeyboardButton(text="📗 Профиль")],
        [KeyboardButton(text="🔙 Вернуться в меню")]
    ],
    resize_keyboard=True
)


class UserState(StatesGroup):
    choosing_exam = State()
    choosing_level = State()
    solving_task = State()


class TaskManager:
    def __init__(self):
        self._last_topic = None
        self._used_tasks = {}  # Словарь для отслеживания использованных заданий по темам
        
    def get_new_task(self, exam_type: str, level: str) -> dict:
        """Получает новую задачу с чередованием тем"""
        try:
            # Получаем все доступные задачи для данного экзамена и уровня
            available_problems = get_adaptive_problem(exam_type, level)
            
            if not available_problems:
                return None
            
            # Группируем задачи по темам
            problems_by_topic = {}
            for problem in available_problems:
                topic = problem['topic']
                if topic not in problems_by_topic:
                    problems_by_topic[topic] = []
                problems_by_topic[topic].append(problem)
            
            # Выбираем тему, отличную от предыдущей
            available_topics = list(problems_by_topic.keys())
            if self._last_topic in available_topics:
                available_topics.remove(self._last_topic)
            
            if not available_topics:  # Если нет других тем, сбрасываем историю
                self._last_topic = None
                available_topics = list(problems_by_topic.keys())
            
            # Выбираем случайную тему
            new_topic = random.choice(available_topics)
            
            # Инициализируем множество использованных задач для новой темы
            if new_topic not in self._used_tasks:
                self._used_tasks[new_topic] = set()
            
            # Выбираем неиспользованную задачу из выбранной темы
            available_tasks = [
                task for task in problems_by_topic[new_topic] 
                if task['id'] not in self._used_tasks[new_topic]
            ]
            
            if not available_tasks:  # Если все задачи темы использованы
                self._used_tasks[new_topic].clear()  # Сбрасываем историю для этой темы
                available_tasks = problems_by_topic[new_topic]
            
            task = random.choice(available_tasks)
            
            # Обновляем историю
            self._used_tasks[new_topic].add(task['id'])
            self._last_topic = new_topic
            
            return task
            
        except Exception as e:
            logger.error(f"Error in get_new_task: {e}")
            return None

# Создаем глобальный экземпляр TaskManager
task_manager = TaskManager()

# Расширенная база задач по геометрии
geometry_problems = [
    # Планиметрия
    {
        "id": "p1",
        "topic": "Геометрия",
        "category": "Планиметрия",
        "exam_type": "ЕГЭ",
        "level": "профиль",
        "complexity": 2,
        "text": """📏 *Задача на окружность*

В окружности радиуса 13:
• Хорда AB = 24
• Точка C лежит на меньшей дуге AB
• ∠ACB = 60°

Найдите расстояние от центра окружности до хорды AB.""",
        "answer": "5",
        "hints": [
            "Вспомните теорему о связи радиуса и расстояния до хорды",
            "Используйте теорему Пифагора",
            "R² = h² + (AB/2)²"
        ],
        "solution": """1) Пусть h - искомое расстояние
2) По теореме о связи радиуса и расстояния до хорды:
   R² = h² + (AB/2)²
3) 13² = h² + 12²
4) h² = 169 - 144 = 25
5) h = 5"""
    },
    
    # Стереометрия
    {
        "id": "s1",
        "topic": "Геометрия",
        "category": "Стереометрия",
        "exam_type": "ЕГЭ",
        "level": "профиль",
        "complexity": 3,
        "text": """📐 *Задача на пирамиду*

В правильной четырехугольной пирамиде SABCD:
• Сторона основания AC = 8
• Боковое ребро SA = 5
• Угол между SA и плоскостью основания равен 60°

Найдите объем пирамиды.""",
        "answer": "32",
        "hints": [
            "Высота пирамиды = SA * sin(60°)",
            "Площадь основания = AC²",
            "V = ⅓ * S_осн * h"
        ],
        "solution": """1) h = SA * sin(60°) = 5 * √3/2
2) S_осн = 8² = 64
3) V = ⅓ * 64 * (5√3/2) = 32"""
    },
    
    # Векторы
    {
        "id": "v1",
        "topic": "Геометрия",
        "category": "Векторы",
        "exam_type": "ЕГЭ",
        "level": "профиль",
        "complexity": 3,
        "text": """➡️ *Задача на векторы*

В кубе ABCDA₁B₁C₁D₁:
• Ребро куба равно 2
• Точка M - середина ребра AA₁
• Точка K - середина ребра CC₁

Найдите скалярное произведение векторов AM и BK.""",
        "answer": "2",
        "hints": [
            "Введите систему координат",
            "Найдите координаты точек A, M, B, K",
            "Используйте формулу скалярного произведения"
        ],
        "solution": """1) A(0,0,0), B(2,0,0), C(2,2,0)
2) M(0,0,1), K(2,2,1)
3) AM = (0,0,1), BK = (0,2,1)
4) AM·BK = 0 + 0 + 1 = 2"""
    },
    
    # Координаты
    {
        "id": "k1",
        "topic": "Геометрия",
        "category": "Координаты",
        "exam_type": "ЕГЭ",
        "level": "профиль",
        "complexity": 2,
        "text": """📍 *Задача на координаты*

В пространстве даны точки:
• A(1,2,3)
• B(4,5,6)
• C(7,8,9)

Найдите площадь треугольника ABC.""",
        "answer": "7",
        "hints": [
            "Используйте векторное произведение",
            "S = ½|AB × AC|",
            "Не забудьте про формулу длины вектора"
        ],
        "solution": """1) AB = (3,3,3)
2) AC = (6,6,6)
3) AB × AC = (0,0,0)
4) S = ½ * √(0² + 0² + 0²) = 7"""
    }
]

async def format_task_message(problem: dict) -> str:
    """Форматирует сообщение с задачей"""
    difficulty_map = {
        1: "🟢 Базовый уровень",
        2: "🟡 Средний уровень",
        3: "🔴 Сложный уровень"
    }
    
    topic_icon = TOPIC_ICONS.get(problem['topic'], "📚")
    difficulty = difficulty_map.get(problem['complexity'], "⚪ Не указана")
    
    header = f"{'✨'*20}\n"
    footer = f"\n{'✨'*20}"
    
    # Добавляем подсказку по формату ответа
    answer_format_hint = {
        "integer": "Введите целое число",
        "float": "Введите число (можно дробное)",
        "trig": "Введите точное значение (например, √2/2 или 0.707)",
        "string": "Введите ответ"
    }.get(problem.get('answer_type', 'string'), "")
    
    message = (
        f"{header}"
        f"{topic_icon} *{problem['topic']}*\n"
        f"📚 {problem['exam_type']} {problem['level']}\n"
        f"📊 {difficulty}\n\n"
        f"{problem['text']}\n"
        f"{footer}\n\n"
        f"💡 Формат ответа: _{answer_format_hint}_\n"
        f"❓ Подсказка: используйте /hint"
    )
    return message

def get_problem(exam_type: str, level: str) -> dict:
    """Временная функция для получения задачи"""
    suitable_problems = [
        p for p in geometry_problems 
        if p["exam_type"].lower() == exam_type.lower() and 
           p["level"].lower() == level.lower()
    ]
    return random.choice(suitable_problems) if suitable_problems else None


async def format_stats_message(stats: dict) -> str:
    total_attempts = stats['total_attempts']
    solved = stats['solved']
    accuracy = stats['accuracy']
    level = stats['level']
    rank = stats['rank']
    progress = max(0, stats['progress'])

    # Прогресс-бар
    progress_bar_length = 10
    filled = int(progress * progress_bar_length / 100)
    progress_bar = "▰" * filled + "▱" * (progress_bar_length - filled)

    stats_message = (
        f"📊 *Ваша статистика:*\n\n"
        f"{rank}\n"
        f"Уровень: {level} {progress_bar} {progress}%\n\n"
        f"📝 Всего попыток: `{total_attempts}`\n"
        f"✅ Решено задач: `{solved}`\n"
        f"🎯 Точность: `{accuracy}%`\n\n"
    )

    # Добавляем мотивационное сообщение
    if accuracy >= 90:
        stats_message += "🌟 _Великолепная точность! Вы настоящий профессионал!_\n"
    elif accuracy >= 80:
        stats_message += "✨ _Отличный результат! Продолжайте в том же духе!_\n"
    elif accuracy >= 70:
        stats_message += "💫 _Хорошая работа! Вы на верном пути!_\n"
    else:
        stats_message += "💪 _Практика ведет к совершенству! Не сдавайтесь!_\n"

    # Добавляем информацию о следующем звании
    next_ranks = {
        "🌱 Новичок": ("📚 Ученик", "решите больше задач"),
        "📚 Ученик": ("🎯 Практик", "достигните точности 70%"),
        "🎯 Практик": ("💫 Знаток", "достигните точности 75%"),
        "💫 Знаток": ("🏆 Мастер", "достигните точности 80%"),
        "🏆 Мастер": ("👑 Гроссмейстер", "достигните точности 85%"),
        "👑 Гроссмейстер": ("⭐ Легенда", "достигните точности 90%"),
        "⭐ Легенда": ("🌟 Профессор", "достигните точности 95%"),
    }

    if rank in next_ranks:
        next_rank, requirement = next_ranks[rank]
        stats_message += f"\n📈 До звания {next_rank}: {requirement}"

    return stats_message


async def format_achievements_message(achievements: List[Dict]) -> str:
    """Форматирует сообщение с достижениями"""
    if not achievements:
        return (
            "🏆 *Достижения*\n\n"
            "У вас пока нет достижений.\n"
            "Решайте задачи, чтобы получать награды!\n\n"
            "💡 Подсказка: получите первое достижение, решив одну задачу."
        )

    message = "🏆 *Ваши достижения:*\n\n"
    for ach in achievements:
        date = datetime.fromisoformat(ach['obtained_at']).strftime("%d.%m.%Y")
        message += (
            f"{ach['icon']} *{ach['name']}*\n"
            f"└ _{ach['description']}_\n"
            f"└ Получено: `{date}`\n\n"
        )
    return message


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в Math Bot!\n\n"
        "Я помогу вам подготовиться к экзаменам по математике.\n\n"
        "🔹 Выбирайте тип экзамена\n"
        "🔹 Решайте задачи\n"
        "🔹 Следите за прогрессом\n"
        "🔹 Получайте достижения\n\n"
        "Начнем? Выберите действие в меню! 👇",
        reply_markup=main_menu
    )


@router.message(lambda message: message.text == "📝 Выбрать экзамен")
async def choose_exam(message: types.Message, state: FSMContext):
    await state.set_state(UserState.choosing_exam)
    await message.answer("📝 Выберите экзамен:", reply_markup=exam_menu)


@router.message(UserState.choosing_exam)
async def process_exam_choice(message: types.Message, state: FSMContext):
    if message.text in ["📚 ЕГЭ", "📖 ОГЭ"]:
        await state.update_data(exam_type=message.text)
        await state.set_state(UserState.choosing_level)
        await message.answer("📊 Выберите уровень:", reply_markup=level_menu)
    else:
        await message.answer("Пожалуйста, выберите тип экзамена из меню.")


@router.message(UserState.choosing_level)
async def process_level_choice(message: types.Message, state: FSMContext):
    if message.text in ["📘 База", "📗 Профиль"]:
        await state.update_data(level=message.text)
        data = await state.get_data()
        await message.answer(
            f"✅ Выбран {data['exam_type']} ({message.text}).\n"
            "Нажмите '✨ Получить задачу'!",
            reply_markup=main_menu
        )
        await state.set_state(UserState.solving_task)
    else:
        await message.answer("Пожалуйста, выберите уровень из меню.")


@router.message(lambda message: message.text == "✨ Получить задачу")
async def send_task(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        exam_type = data.get('exam_type', '').replace('📚 ', '').replace('📖 ', '')
        level = data.get('level', '').replace('📘 ', '').replace('📗 ', '').lower()

        if not exam_type or not level:
            await message.answer(
                "⚠️ Сначала выберите тип экзамена!",
                reply_markup=main_menu
            )
            return

        problem = get_problem(exam_type, level)
        
        if not problem:
            await message.answer(
                "😔 Не удалось найти задачу. Попробуйте перезапустить бота командой /start",
                reply_markup=main_menu
            )
            return

        await state.update_data(current_problem=problem)
        
        task_message = (
            f"{'='*30}\n"
            f"📚 {problem['topic']}\n"
            f"📊 Сложность: {'🟢' if problem['complexity'] == 1 else '🟡' if problem['complexity'] == 2 else '🔴'}\n\n"
            f"{problem['text']}\n"
            f"{'='*30}"
        )
        
        await message.answer(task_message, reply_markup=main_menu)
        
    except Exception as e:
        logger.error(f"Error in send_task: {e}", exc_info=True)
        await message.answer(
            "😔 Произошла ошибка. Попробуйте перезапустить бота командой /start",
            reply_markup=main_menu
        )


@router.message(UserState.solving_task)
async def check_answer(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        problem = data.get('current_problem')
        
        if not problem:
            await message.answer("Сначала получите задачу!", reply_markup=main_menu)
            return

        user_answer = message.text.strip().lower().replace(',', '.')
        correct_answer = str(problem['answer']).lower()
        
        is_correct = user_answer == correct_answer
        update_user_stats(message.from_user.id, is_correct)

        if is_correct:
            await message.answer(
                "✅ Правильно! Молодец!\n\n"
                "Нажмите '✨ Получить задачу' для следующего задания.",
                reply_markup=main_menu
            )
        else:
            await message.answer(
                f"❌ Неправильно.\n\n"
                f"Правильный ответ: {problem['answer']}\n"
                f"Подсказка: {problem['hint']}\n\n"
                f"Нажмите '✨ Получить задачу' для следующего задания.",
                reply_markup=main_menu
            )

    except Exception as e:
        logger.error(f"Error in check_answer: {e}", exc_info=True)
        await message.answer(
            "😔 Произошла ошибка при проверке ответа.",
            reply_markup=main_menu
        )


@router.message(lambda message: message.text == "📊 Статистика")
async def show_stats(message: types.Message):
    stats = get_user_stats(message.from_user.id)
    
    await message.answer(
        "📊 Ваша статистика:\n\n"
        f"📝 Всего попыток: {stats['total_attempts']}\n"
        f"✅ Правильных ответов: {stats['correct_answers']}\n"
        f"🎯 Точность: {stats['accuracy']}%\n"
        f"🔥 Текущая серия: {stats['current_streak']}\n"
        f"🏆 Лучшая серия: {stats['max_streak']}",
        reply_markup=main_menu
    )


@router.message(lambda message: message.text == "💡 Помощь")
async def show_help(message: types.Message):
    await message.answer(
        "📌 Как пользоваться ботом:\n\n"
        "1️⃣ Выберите тип экзамена и уровень\n"
        "2️⃣ Нажмите '✨ Получить задачу'\n"
        "3️⃣ Решите задачу и введите ответ\n"
        "4️⃣ Проверьте статистику\n\n"
        "📝 Формат ответов:\n"
        "• Целые числа: 42\n"
        "• Дробные числа: 3.14\n"
        "• Дроби: 1/2\n"
        "• Тригонометрия: √2/2 или 0.707",
        reply_markup=main_menu
    )


@router.message(lambda message: message.text == "🏆 Достижения")
async def show_achievements(message: types.Message):
    """Показывает достижения пользователя"""
    try:
        achievements = get_user_achievements(message.from_user.id)
        achievements_message = await format_achievements_message(achievements)
        await message.answer(achievements_message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error showing achievements: {e}")
        await message.answer(
            "😔 *Произошла ошибка*\n\n"
            "Не удалось загрузить достижения.",
            parse_mode="Markdown"
        )


def normalize_number(value):
    """Нормализует числовое значение"""
    try:
        # Пробуем преобразовать в float
        num = float(value)
        # Если это целое число, возвращаем как int
        if num.is_integer():
            return int(num)
        # Иначе возвращаем float с ограничением знаков после запятой
        return round(num, 4)
    except ValueError:
        return value


def check_answers_equality(user_answer: str, correct_answer: str, answer_type: str = "string") -> bool:
    """Проверяет равенство ответов с учетом типа ответа"""
    try:
        # Очищаем ответ пользователя от пробелов
        user_answer = user_answer.strip()
        
        if answer_type == "integer":
            return int(user_answer) == int(correct_answer)
            
        elif answer_type == "float":
            return abs(float(user_answer) - float(correct_answer)) < 0.001
            
        elif answer_type == "trig":
            # Нормализуем ответы
            user_answer = user_answer.replace(" ", "").lower()
            correct_answer = correct_answer.replace(" ", "").lower()
            
            # Проверяем точное совпадение
            if user_answer == correct_answer:
                return True
                
            # Проверяем числовое значение
            try:
                if "√" in correct_answer:
                    if "√2/2" in correct_answer:
                        correct_value = 0.707
                    elif "√3/2" in correct_answer:
                        correct_value = 0.866
                    else:
                        return user_answer == correct_answer
                    
                    user_value = float(user_answer)
                    return abs(user_value - correct_value) < 0.01
                
                if "/" in correct_answer:
                    num, den = map(int, correct_answer.split("/"))
                    correct_value = num / den
                    user_value = float(user_answer)
                    return abs(user_value - correct_value) < 0.01
                    
            except (ValueError, ZeroDivisionError):
                pass
                
            return False
            
        # Для остальных типов - строгое строковое сравнение
        return user_answer == correct_answer
        
    except Exception as e:
        logger.error(f"Error in check_answers_equality: {e}")
        return False


@router.message(lambda message: message.text == "📚 Темы")
async def show_topics(message: types.Message):
    """Показывает меню выбора тем"""
    await message.answer(
        "Выберите тему для практики:",
        reply_markup=topics_menu
    )

@router.message(lambda message: message.text.endswith("Вернуться в меню"))
async def return_to_main_menu(message: types.Message):
    """Возвращает в главное меню"""
    await message.answer(
        "Вы вернулись в главное меню",
        reply_markup=main_menu
    )