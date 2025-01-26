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


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            "📖 *Добро пожаловать в MathExamBot!*\n"
            "Я помогу подготовиться к ЕГЭ и ОГЭ по математике.\n\n"
            "❗ *Как давать ответы:*\n"
            "- Числа: **12** или **5.67**\n"
            "- Дроби: **3/4**\n"
            "- Множество ответов: **2; -5**\n"
            "- Текст: пишите разборчиво!",
            reply_markup=main_menu,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


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


@router.message(lambda message: message.text == "📚 Получить задачу", UserState.solving_task)
async def send_task(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        problem = get_random_problem(data['exam_type'], data.get('level', 'база'))

        if problem:
            await state.update_data(current_problem=problem)
            await message.answer(
                f"🔍 *{problem['topic']} ({problem['exam_type']}, {problem['level']})*\n\n"
                f"{problem['text']}\n\n"
                f"✏️ Введите ответ:",
                parse_mode="Markdown"
            )
        else:
            await message.answer("😢 Задачи закончились. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка при получении задачи: {e}")
        await message.answer("⚠️ Не удалось получить задачу. Попробуйте позже.")


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
    """Показ статистики пользователя"""
    try:
        stats = get_user_stats(message.from_user.id)

        # Основная статистика
        total_attempts = stats.get('total_attempts', 0)
        solved = stats.get('solved', 0)
        accuracy = (solved / total_attempts * 100) if total_attempts > 0 else 0

        # Формируем текст статистики
        stats_text = (
            "📊 *Ваша статистика:*\n\n"
            f"📝 Всего попыток: {total_attempts}\n"
            f"✅ Решено задач: {solved}\n"
            f"📈 Точность: {accuracy:.1f}%"
        )

        # Добавляем статистику по темам, если она есть
        if topics := stats.get('topics'):
            stats_text += "\n\n📚 *По темам:*"
            for topic, count in topics.items():
                stats_text += f"\n• {topic}: {count}"

        await message.answer(stats_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка при показе статистики: {e}")
        await message.answer("⚠️ Не удалось загрузить статистику. Попробуйте позже.")


@router.message(lambda message: message.text == "🏆 Достижения")
async def show_achievements(message: types.Message):
    """Показывает достижения пользователя"""
    try:
        achievements = get_user_achievements(message.from_user.id)

        if not achievements:
            await message.answer(
                "🏆 У вас пока нет достижений.\n"
                "Решайте задачи, чтобы получать новые достижения!"
            )
            return

        # Формируем текст с достижениями
        text = "🏆 *Ваши достижения:*\n\n"
        for ach in achievements:
            text += f"{ach['icon']} *{ach['name']}*\n"
            text += f"_{ach['description']}_\n"
            text += f"Получено: {ach['obtained_at']}\n\n"

        await message.answer(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error showing achievements: {e}")
        await message.answer("Произошла ошибка при загрузке достижений.")


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
    # Если пользователь запросил статистику во время решения
    if message.text == "📊 Статистика":
        await show_stats(message)
        return

    try:
        data = await state.get_data()
        problem = data.get('current_problem')
        if not problem:
            await message.answer("Сначала запросите задачу через меню!")
            return

        # Нормализуем ответ пользователя
        user_answer = message.text.strip().replace(',', '.')

        # Проверяем ответ
        is_correct = check_answers_equality(
            user_answer,
            problem['answer'],
            problem['topic']
        )

        # Обновляем статистику с учетом правильности ответа
        update_user_stats(message.from_user.id, is_correct)

        if is_correct:
            await message.answer("✅ *Верно!* Молодец! 😊", parse_mode="Markdown")
        else:
            hint_text = (
                f"❌ *Неверно.*\n"
                f"Ваш ответ: {user_answer}\n"
                f"Правильный ответ: {problem['answer']}\n\n"
                f"{problem['hint']}"
            )
            await message.answer(hint_text, parse_mode="Markdown")

        # Показываем статистику после ответа
        await show_stats(message)
        # Отправляем следующую задачу
        await send_task(message, state)

        # После обновления статистики проверяем новые достижения
        new_achievements = check_achievements(message.from_user.id)
        if new_achievements:
            achievements_text = "🎉 *Получены новые достижения:*\n\n"
            for ach in new_achievements:
                achievements_text += f"{ach['icon']} *{ach['name']}*\n"
                achievements_text += f"_{ach['description']}_\n\n"
            await message.answer(achievements_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка при проверке ответа: {e}", exc_info=True)
        await message.answer(
            "⚠️ Примеры правильного формата ответа:\n"
            "- Целые числа: 50\n"
            "- Десятичные дроби: 50.24\n"
            "- Дроби: 1/2\n"
            "- Несколько ответов: 2; -5\n"
            "- Вероятности: 0.5 или 1/2"
        )