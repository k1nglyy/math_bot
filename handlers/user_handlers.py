from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.database import (
    get_random_problem,
    update_user_stats,
    get_user_stats,
    get_user_achievements,
    check_achievements
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
    one_time_keyboard=True  # Скрывать клавиатуру после выбора
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
    """Форматирует сообщение статистики с адаптивными сообщениями"""
    total_attempts = stats['total_attempts']
    solved = stats['solved']
    accuracy = stats['accuracy']

    # Определяем иконку в зависимости от точности
    if accuracy >= 90:
        accuracy_icon = "🎯"
        level = "excellent"
    elif accuracy >= 70:
        accuracy_icon = "🎪"
        level = "good"
    elif accuracy >= 50:
        accuracy_icon = "🎱"
        level = "average"
    else:
        accuracy_icon = "🎲"
        level = "low"

    # Мотивационные сообщения в зависимости от уровня
    motivation_messages = {
        "excellent": [
            "Потрясающий результат! Так держать! 🌟",
            "Вы настоящий математический гений! ✨",
            "Великолепная работа! Продолжайте в том же духе! 🏆",
            "Ваша точность впечатляет! 🎯"
        ],
        "good": [
            "Хороший результат! Вы на верном пути! 🌟",
            "Отличная работа! Есть куда расти! 💪",
            "Вы делаете успехи! Продолжайте практиковаться! 📈",
            "Неплохой результат! Двигайтесь дальше! 🎯"
        ],
        "average": [
            "Неплохое начало! Регулярная практика поможет улучшить результат! 💪",
            "Есть пространство для роста! Не сдавайтесь! 🌱",
            "Продолжайте тренироваться, и результат обязательно улучшится! 📚",
            "С каждой решённой задачей вы становитесь сильнее! 💡"
        ],
        "low": [
            "Главное - не сдаваться! Каждая решённая задача - это шаг вперёд! 🌱",
            "Начало положено! Регулярные тренировки помогут улучшить результат! 💪",
            "Не переживайте! Математика требует времени и практики! 📚",
            "Пробуйте разные задачи и учитесь на ошибках! 💡"
        ]
    }

    # Рекомендации в зависимости от количества решенных задач
    if total_attempts < 10:
        recommendation = "💡 Попробуйте решить больше задач, чтобы увидеть свой реальный уровень!"
    elif accuracy < 50:
        recommendation = "💡 Обратите внимание на подсказки после неверных ответов, они помогут улучшить результат!"
    elif accuracy < 70:
        recommendation = "💡 Попробуйте решать задачи разных типов, чтобы расширить свои знания!"
    elif accuracy < 90:
        recommendation = "💡 Вы почти достигли мастерства! Осталось совсем немного!"
    else:
        recommendation = "💡 Попробуйте более сложные задачи, чтобы продолжить развитие!"

    # Прогресс до следующего уровня точности
    next_level = None
    if accuracy < 50:
        next_level = 50
    elif accuracy < 70:
        next_level = 70
    elif accuracy < 90:
        next_level = 90

    progress_message = ""
    if next_level:
        points_needed = next_level - accuracy
        progress_message = f"\n📊 До следующего уровня: {points_needed:.1f}%"

    stats_message = (
        f"📊 *Ваша статистика:*\n\n"
        f"📝 Всего попыток: `{total_attempts}`\n"
        f"✅ Решено задач: `{solved}`\n"
        f"{accuracy_icon} Точность: `{accuracy}%`"
        f"{progress_message}\n\n"
        f"_{random.choice(motivation_messages[level])}_\n\n"
        f"{recommendation}"
    )

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
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 *Добро пожаловать в Math Bot!*\n\n"
        "Я помогу вам подготовиться к экзаменам по математике.\n\n"
        "🔹 Выбирайте тип экзамена\n"
        "🔹 Решайте задачи\n"
        "🔹 Следите за прогрессом\n"
        "🔹 Получайте достижения\n\n"
        "Начнем? Выберите действие в меню! 👇"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu)


@router.message(lambda message: message.text == "🎓 Выбрать экзамен")
async def choose_exam(message: types.Message, state: FSMContext):
    await message.answer("📝 Выберите экзамен:", reply_markup=exam_menu)
    await state.set_state(UserState.choosing_exam)


@router.message(lambda message: message.text in ["ЕГЭ", "ОГЭ"], UserState.choosing_exam)
async def set_exam(message: types.Message, state: FSMContext):
    exam_type = "ЕГЭ" if message.text == "ЕГЭ" else "ОГЭ"
    await state.update_data(exam_type=exam_type)

    if exam_type == "ОГЭ":
        await state.update_data(level="база")
        await message.answer("✅ Выбран ОГЭ (базовый уровень).\nНажмите '📚 Получить задачу'!", reply_markup=main_menu)
        await state.set_state(UserState.solving_task)
    else:
        await message.answer("📊 Выберите уровень:", reply_markup=level_menu)
        await state.set_state(UserState.choosing_level)


@router.message(lambda message: message.text in ["База", "Профиль"], UserState.choosing_level)
async def set_level(message: types.Message, state: FSMContext):
    level = message.text.lower()
    await state.update_data(level=level)
    data = await state.get_data()
    await message.answer(
        f"✅ Выбран {data['exam_type']} ({level}).\nНажмите '📚 Получить задачу'!",
        reply_markup=main_menu
    )
    await state.set_state(UserState.solving_task)


@router.message(lambda message: message.text == "📚 Получить задачу")
async def send_task(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        exam_type = data.get('exam_type')
        level = data.get('level')
        last_topic = data.get('last_topic')  # Получаем тему предыдущей задачи

        if not exam_type or not level:
            await message.answer(
                "⚠️ *Сначала выберите тип экзамена!*\n\n"
                "Нажмите '🎓 Выбрать экзамен'",
                parse_mode="Markdown",
                reply_markup=main_menu
            )
            return

        problem = get_random_problem(exam_type, level, last_topic)
        if not problem:
            await message.answer(
                "😔 *Извините, не удалось найти подходящую задачу.*\n\n"
                "Попробуйте выбрать другой тип экзамена.",
                parse_mode="Markdown",
                reply_markup=main_menu
            )
            return

        # Сохраняем текущую тему для следующего запроса
        await state.update_data(last_topic=problem['topic'])
        await state.update_data(current_problem=problem)

        task_message = (
            f"{problem['topic']} ({exam_type}, {level})\n"
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
    stats = get_user_stats(message.from_user.id)
    stats_message = await format_stats_message(stats)
    await message.answer(stats_message, parse_mode="Markdown", reply_markup=main_menu)


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
    if message.text == "📊 Статистика":
        await show_stats(message)
        return

    try:
        data = await state.get_data()
        problem = data.get('current_problem')
        if not problem:
            await message.answer(
                "⚠️ *Сначала запросите задачу!*\n\n"
                "Нажмите '📚 Получить задачу'",
                parse_mode="Markdown",
                reply_markup=main_menu
            )
            return

        user_answer = message.text.strip().replace(',', '.')
        is_correct = check_answers_equality(user_answer, problem['answer'], problem['topic'])
        update_user_stats(message.from_user.id, is_correct)

        if is_correct:
            await message.answer(
                "✨ *Отлично!* Правильный ответ! 🎉\n\n"
                "_Так держать!_",
                parse_mode="Markdown",
                reply_markup=main_menu
            )
        else:
            hint_text = (
                f"❌ *Неверно*\n\n"
                f"Ваш ответ: `{user_answer}`\n"
                f"Правильный ответ: `{problem['answer']}`\n\n"
                f"💡 *Подсказка:*\n{problem['hint']}"
            )
            await message.answer(hint_text, parse_mode="Markdown", reply_markup=main_menu)

        new_achievements = check_achievements(message.from_user.id)
        if new_achievements:
            achievements_text = (
                "🎉 *Поздравляем!*\n\n"
                "*Получены новые достижения:*\n\n"
            )
            for ach in new_achievements:
                achievements_text += f"{ach['icon']} *{ach['name']}*\n└ _{ach['description']}_\n\n"
            await message.answer(achievements_text, parse_mode="Markdown", reply_markup=main_menu)

        await show_stats(message)
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
            parse_mode="Markdown",
            reply_markup=main_menu
        )