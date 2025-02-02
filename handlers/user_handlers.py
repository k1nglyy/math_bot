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

router = Router()
logger = logging.getLogger(__name__)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎓 Выбрать экзамен"), KeyboardButton(text="📚 Получить задачу")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь"), KeyboardButton(text="🏆 Достижения")]
    ],
    resize_keyboard=True,
)

exam_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ЕГЭ"), KeyboardButton(text="ОГЭ")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

level_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="База"), KeyboardButton(text="Профиль")],
        [KeyboardButton(text="🔙 Назад")]
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


async def format_task_message(problem: dict) -> str:
    """Форматирует сообщение с задачей"""
    topic_icons = {
        "Алгебра": "📐",
        "Геометрия": "📏",
        "Теория вероятностей": "🎲",
        "Статистика": "📊"
    }

    difficulty_stars = "⭐" * problem["complexity"]
    topic_icon = topic_icons.get(problem["topic"], "📚")

    message = (
        f"{topic_icon} *{problem['topic']}* ({problem['exam_type']}, {problem['level']})\n"
        f"Сложность: {difficulty_stars}\n\n"
        f"{problem['text']}\n\n"
        f"✏️ Введите ответ:"
    )
    return message


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
        "👋 Привет! Я бот для подготовки к ЕГЭ и ОГЭ по математике.\n\n"
        "🎓 Выберите экзамен, к которому хотите подготовиться, "
        "затем нажмите '📚 Получить задачу' чтобы начать решать задания.\n\n"
        "📊 В разделе 'Статистика' вы можете отслеживать свой прогресс.\n\n"
        "Удачи в подготовке! 🍀",
        reply_markup=main_menu
    )
    await state.set_state(UserState.choosing_exam)


@router.message(lambda message: message.text == "🎓 Выбрать экзамен")
async def choose_exam(message: types.Message, state: FSMContext):
    await state.set_state(UserState.choosing_exam)
    await message.answer(
        "📝 Выберите экзамен:",
        reply_markup=exam_menu
    )


@router.message(UserState.choosing_exam)
async def process_exam_choice(message: types.Message, state: FSMContext):
    if message.text == "📚 Получить задачу":
        await send_task(message, state)
        return
    elif message.text == "📊 Статистика":
        await show_stats(message)
        return

    if message.text not in ["ЕГЭ", "ОГЭ"]:
        await message.answer(
            "Пожалуйста, выберите ЕГЭ или ОГЭ",
            reply_markup=exam_menu
        )
        return

    await state.update_data(exam_type=message.text)

    if message.text == "ЕГЭ":
        await state.set_state(UserState.choosing_level)
        await message.answer(
            "📊 Выберите уровень:",
            reply_markup=level_menu
        )
    else:
        await state.update_data(level="база")
        await state.set_state(UserState.solving_task)
        await message.answer(
            f"✅ Выбран {message.text}.\nНажмите '📚 Получить задачу'!",
            reply_markup=main_menu
        )


@router.message(UserState.choosing_level)
async def process_level_choice(message: types.Message, state: FSMContext):
    if message.text == "📚 Получить задачу":
        await send_task(message, state)
        return
    elif message.text == "📊 Статистика":
        await show_stats(message)
        return

    if message.text.lower() not in ["база", "профиль"]:
        await message.answer(
            "Пожалуйста, выберите 'База' или 'Профиль'",
            reply_markup=level_menu
        )
        return

    await state.update_data(level=message.text.lower())
    await state.set_state(UserState.solving_task)

    await message.answer(
        f"✅ Выбран ЕГЭ ({message.text.lower()}).\nНажмите '📚 Получить задачу'!",
        reply_markup=main_menu
    )


@router.message(lambda message: message.text == "📚 Получить задачу")
async def send_task(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if not data.get('exam_type'):
        await state.set_state(UserState.choosing_exam)
        await message.answer(
            "⚠️ Сначала выберите тип экзамена!\n\n"
            "Нажмите '🎓 Выбрать экзамен'",
            reply_markup=exam_menu
        )
        return

    if not data.get('level') and data.get('exam_type') == "ЕГЭ":
        await state.set_state(UserState.choosing_level)
        await message.answer(
            "📊 Выберите уровень:",
            reply_markup=level_menu
        )
        return

    try:
        exam_type = data.get('exam_type')
        level = data.get('level')
        last_topic = data.get('last_topic')

        if not exam_type or not level:
            await state.set_state(UserState.choosing_exam)
            await message.answer(
                "⚠️ *Сначала выберите тип экзамена!*\n\n"
                "Нажмите '🎓 Выбрать экзамен'",
                parse_mode="Markdown",
                reply_markup=main_menu
            )
            return

        # Получаем статистику пользователя для адаптивной сложности
        user_stats = get_user_stats(message.from_user.id)
        problem = get_adaptive_problem(exam_type, level, last_topic, user_stats)

        if not problem:
            await message.answer(
                "😔 *Извините, не удалось найти подходящую задачу.*\n\n"
                "Попробуйте выбрать другой тип экзамена.",
                parse_mode="Markdown",
                reply_markup=main_menu
            )
            return

        await state.update_data(last_topic=problem['topic'])
        await state.update_data(current_problem=problem)

        task_message = (
            f"📏 *{problem['topic']}* ({exam_type}, {level})\n"
            f"Сложность: {'⭐' * problem['complexity']}\n\n"
            f"{problem['text']}\n\n"
            f"✏️ Введите ответ:"
        )
        await message.answer(task_message, parse_mode="Markdown", reply_markup=main_menu)

    except Exception as e:
        logger.error(f"Error sending task: {e}")
        await message.answer(
            "😔 *Произошла ошибка*\n\n"
            "Попробуйте получить задачу еще раз.",
            parse_mode="Markdown",
            reply_markup=main_menu
        )


@router.message(lambda message: message.text == "ℹ️ Помощь")
async def show_help(message: types.Message):
    await message.answer(
        "📌 *Инструкция:*\n"
        "1. Выберите экзамен и уровень.\n"
        "2. Получайте задачи и решайте их.\n"
        "3. *Форматы ответов:*\n"
        "   - Числа: **5**, **3.14**\n"
        "   - Дроби: **2/3**\n"
        "   - Бесконечные дроби: **0.33** (округление) или **1/3**\n"
        "   - Множество корней: **1; -2**\n\n"
        "❗ Примеры:\n"
        "- Ответ 0.3333... → введите 0.33 или 1/3\n"
        "- Ответ 2.666... → введите 2.67 или 8/3",
        parse_mode="Markdown"
    )


@router.message(lambda message: message.text == "🔙 Назад")
async def go_back(message: types.Message, state: FSMContext):
    """Обработка кнопки Назад"""
    current_state = await state.get_state()

    if current_state == UserState.choosing_level.state:
        # Возврат к выбору экзамена
        await message.answer("📝 Выберите экзамен:", reply_markup=exam_menu)
        await state.set_state(UserState.choosing_exam)
    else:
        # Возврат в главное меню
        await state.clear()
        await message.answer("Выберите действие:", reply_markup=main_menu)


@router.message(lambda message: message.text == "📊 Статистика")
async def show_stats(message: types.Message):
    """Показывает статистику пользователя"""
    try:
        logger.info(f"User {message.from_user.id} requested stats")
        stats = get_user_stats(message.from_user.id)

        # Прогресс-бар
        progress = min(100, stats.get('progress', 0))
        progress_bar_length = 10
        filled = int(progress * progress_bar_length / 100)
        progress_bar = "▰" * filled + "▱" * (progress_bar_length - filled)

        stats_message = (
            f"📊 *Ваша статистика:*\n\n"
            f"{stats.get('rank', '🌱 Новичок')}\n"
            f"Уровень: {stats.get('level', 1)} {progress_bar} {progress}%\n\n"
            f"📝 Всего попыток: `{stats.get('total_attempts', 0)}`\n"
            f"✅ Решено задач: `{stats.get('solved', 0)}`\n"
            f"🎯 Точность: `{stats.get('accuracy', 0)}%`\n\n"
        )

        # Добавляем мотивационное сообщение
        accuracy = stats.get('accuracy', 0)
        if accuracy >= 90:
            stats_message += "🌟 _Великолепная точность! Вы настоящий профессионал!_\n"
        elif accuracy >= 80:
            stats_message += "✨ _Отличный результат! Продолжайте в том же духе!_\n"
        elif accuracy >= 70:
            stats_message += "💫 _Хорошая работа! Вы на верном пути!_\n"
        else:
            stats_message += "💪 _Практика ведет к совершенству! Не сдавайтесь!_\n"

        # Добавляем информацию о следующем ранге
        ranks = {
            "🌱 Новичок": ("📚 Ученик", "решите больше задач"),
            "📚 Ученик": ("🎯 Практик", "достигните точности 70%"),
            "🎯 Практик": ("💫 Знаток", "достигните точности 75%"),
            "💫 Знаток": ("🏆 Мастер", "достигните точности 80%"),
            "🏆 Мастер": ("👑 Гроссмейстер", "достигните точности 85%"),
            "👑 Гроссмейстер": ("⭐ Легенда", "достигните точности 90%"),
            "⭐ Легенда": ("🌟 Профессор", "достигните точности 95%"),
        }

        current_rank = stats.get('rank', "🌱 Новичок")
        if current_rank in ranks:
            next_rank, requirement = ranks[current_rank]
            stats_message += f"\n📈 До звания {next_rank}: {requirement}"

        logger.info(f"Sending stats to user {message.from_user.id}: {stats}")
        await message.answer(stats_message, parse_mode="Markdown", reply_markup=main_menu)

    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await message.answer(
            "😔 Произошла ошибка при получении статистики.\n"
            "Попробуйте позже.",
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


def check_answers_equality(user_answer, correct_answer, problem_type):
    """Проверяет равенство ответов с учетом типа задачи"""
    try:
        # Для задач с несколькими ответами
        if ";" in str(correct_answer):
            user_parts = [p.strip() for p in str(user_answer).split(";")]
            correct_parts = [p.strip() for p in str(correct_answer).split(";")]

            if len(user_parts) != len(correct_parts):
                return False

            # Сортируем части для правильного сравнения
            user_parts = sorted([normalize_number(p) for p in user_parts])
            correct_parts = sorted([normalize_number(p) for p in correct_parts])

            # Сравниваем каждую пару значений
            for u, c in zip(user_parts, correct_parts):
                if not check_single_answer(u, c, problem_type):
                    return False
            return True

        # Для задач с одним ответом
        return check_single_answer(user_answer, correct_answer, problem_type)

    except Exception as e:
        logger.error(f"Ошибка при сравнении ответов: {e}")
        return False


def check_single_answer(user_value, correct_value, problem_type):
    """Проверяет равенство одиночных ответов"""
    try:
        # Преобразуем строки в числа, если возможно
        user_num = normalize_number(user_value)
        correct_num = normalize_number(correct_value)

        # Если оба значения числовые
        if isinstance(user_num, (int, float)) and isinstance(correct_num, (int, float)):
            # Устанавливаем допуск в зависимости от типа задачи
            tolerance = {
                "Геометрия": 0.1,
                "Теория вероятностей": 0.01,
                "Статистика": 0.01
            }.get(problem_type, 0.01)

            return abs(float(user_num) - float(correct_num)) <= tolerance

        # Если значения не числовые, сравниваем строки
        return str(user_value).strip().lower() == str(correct_value).strip().lower()

    except Exception as e:
        logger.error(f"Ошибка при сравнении одиночных ответов: {e}")
        return False


@router.message(UserState.solving_task)
async def check_answer(message: types.Message, state: FSMContext):
    try:
        # Проверяем специальные команды
        if message.text == "📊 Статистика":
            await show_stats(message)
            return
        elif message.text == "🎓 Выбрать экзамен":
            await state.set_state(UserState.choosing_exam)
            await message.answer("📝 Выберите экзамен:", reply_markup=exam_menu)
            return
        elif message.text == "📚 Получить задачу":
            await send_task(message, state)
            return
        elif message.text == "🏆 Достижения":
            await show_achievements(message)
            return
        elif message.text == "ℹ️ Помощь":
            await show_help(message)
            return

        # Получаем данные о текущей задаче
        data = await state.get_data()
        problem = data.get('current_problem')

        if not problem:
            await send_task(message, state)
            return

        # Проверяем ответ
        user_answer = message.text.strip().replace(',', '.')
        is_correct = check_answers_equality(user_answer, problem['answer'], problem['topic'])
        update_user_stats(message.from_user.id, is_correct)

        if is_correct:
            await message.answer(
                "✨ *Отлично!* Правильный ответ! 🎉\n\n"
                "_Так держать!_",
                parse_mode="Markdown"
            )
        else:
            hint_text = (
                f"❌ *Неверно*\n\n"
                f"Ваш ответ: `{user_answer}`\n"
                f"Правильный ответ: `{problem['answer']}`\n\n"
                f"💡 *Подсказка:*\n{problem['hint']}"
            )
            await message.answer(hint_text, parse_mode="Markdown")

        # Проверяем достижения
        new_achievements = check_achievements(message.from_user.id)
        if new_achievements:
            achievements_text = (
                "🎉 *Поздравляем!*\n\n"
                "*Получены новые достижения:*\n\n"
            )
            for ach in new_achievements:
                achievements_text += f"{ach['icon']} *{ach['name']}*\n└ _{ach['description']}_\n\n"
            await message.answer(achievements_text, parse_mode="Markdown")

        # Показываем статистику
        await show_stats(message)

        # Отправляем новую задачу
        await send_task(message, state)

    except Exception as e:
        logger.error(f"Error checking answer: {e}")
        await message.answer(
            "⚠️ *Примеры правильного формата ответа:*\n\n"
            "🔹 Целые числа: `50`\n"
            "🔹 Десятичные дроби: `50.24`\n"
            "🔹 Дроби: `1/2`\n"
            "🔹 Несколько ответов: `2; -5`\n"
            "🔹 Вероятности: `0.5` или `1/2`",
            parse_mode="Markdown"
        )


ege_10_tasks = {
    "easy": [
        "Простые показательные уравнения (a^x = b)",
        "Определение логарифма",
        "Свойства степеней",
        "Простые тригонометрические выражения (sin, cos)"
    ],

    "medium": [
        "Логарифмы (основные свойства)",
        "Показательные уравнения с одним основанием",
        "Тригонометрические формулы",
        "Формулы приведения"
    ],

    "hard": [
        "Логарифмические уравнения без замен",
        "Показательные неравенства",
        "Тригонометрические уравнения простых видов",
        "Преобразование логарифмических выражений"
    ]
}