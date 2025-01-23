from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from utils.database import (
    save_user_exam,
    get_user_difficulty,
    update_user_stats,
    get_user_stats
)
from utils.problem_bank import ProblemBank

router = Router()
problem_bank = ProblemBank()
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    exam_select = State()
    topic_select = State()
    solving = State()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    try:
        await state.clear()
        await message.answer(
            "📚 Выберите экзамен:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="ОГЭ"), KeyboardButton(text="ЕГЭ")]
                ],
                resize_keyboard=True
            )
        )
        await state.set_state(Form.exam_select)
    except Exception as e:
        logger.error(f"Start error: {str(e)}")
        await message.answer("⚠️ Произошла ошибка, попробуйте позже")


@router.message(Form.exam_select, F.text.in_(["ОГЭ", "ЕГЭ"]))
async def handle_exam_select(message: Message, state: FSMContext):
    """Обработчик выбора экзамена"""
    try:
        await save_user_exam(message.from_user.id, message.text)
        await state.update_data(exam=message.text)

        await message.answer(
            "🔢 Выберите раздел:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Алгебра"), KeyboardButton(text="Геометрия")]
                ],
                resize_keyboard=True
            )
        )
        await state.set_state(Form.topic_select)
    except Exception as e:
        logger.error(f"Exam select error: {str(e)}")
        await message.answer("⚠️ Ошибка выбора экзамена")


@router.message(Form.topic_select, F.text.in_(["Алгебра", "Геометрия"]))
async def handle_topic_select(message: Message, state: FSMContext):
    """Обработчик выбора темы"""
    try:
        user_data = await state.get_data()
        exam = user_data.get("exam", "ОГЭ")
        difficulty = await get_user_difficulty(message.from_user.id)

        problem = problem_bank.get_problem(exam, message.text, difficulty)

        await state.update_data(current_problem=problem)
        await message.answer(
            f"📝 Задача ({exam}, {message.text}):\n{problem['question']}",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.solving)
    except Exception as e:
        logger.error(f"Topic select error: {str(e)}")
        await message.answer("😔 Не удалось загрузить задачу. Попробуйте еще раз")
        await state.clear()


@router.message(Form.solving)
async def handle_solution(message: Message, state: FSMContext):
    """Проверка решения"""
    try:
        user_data = await state.get_data()
        problem = user_data["current_problem"]

        if message.text.strip() == problem["answer"]:
            topic = "Алгебра" if "Алгебра" in problem["question"] else "Геометрия"
            await update_user_stats(message.from_user.id, topic)
            await message.answer("✅ Правильно! Следующая задача:")
            await handle_topic_select(message, state)
        else:
            await message.answer(
                f"❌ Неверно. Правильный ответ: {problem['answer']}\n"
                f"📚 Разбор:\n{problem['solution']}"
            )
    except Exception as e:
        logger.error(f"Solution check error: {str(e)}")
        await message.answer("⚠️ Ошибка проверки решения")


@router.message(Command("stats"))
async def handle_stats(message: Message):
    """Показ статистики"""
    try:
        stats = await get_user_stats(message.from_user.id)
        text = (
            f"📊 Статистика:\n"
            f"Экзамен: {stats.get('exam', 'не выбран')}\n"
            f"Решено алгебры: {stats.get('algebra', 0)}\n"
            f"Решено геометрии: {stats.get('geometry', 0)}\n"
            f"Уровень сложности: {stats.get('difficulty', 1)}"
        )
        await message.answer(text)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        await message.answer("⚠️ Ошибка получения статистики")


@router.message(Form.topic_select, F.text.in_(["Алгебра", "Геометрия"]))
async def handle_topic_select(message: Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = message.from_user.id
        exam = user_data.get("exam", "ОГЭ")
        topic = message.text
        logger.info(f"User {user_id} selected: {exam}/{topic}")
        difficulty = await get_user_difficulty(user_id)
        logger.debug(f"Current difficulty: {difficulty}")
        problem = problem_bank.get_problem(exam, topic, difficulty)
        if not problem:
            raise ValueError("Problem generation failed")
        await state.update_data(current_problem=problem)
        await message.answer(
            f"📝 *Задача ({exam}, {topic}):*\n{problem['question']}",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.solving)

    except Exception as e:
        logger.error(f"Topic selection error: {str(e)}", exc_info=True)
        await message.answer(
            "😔 Не удалось загрузить задачу. Попробуйте:\n"
            "1. Выбрать другой раздел\n"
            "2. Проверить наличие задач в базе\n"
            "3. Перезапустить бота командой /start"
        )
        await state.clear()