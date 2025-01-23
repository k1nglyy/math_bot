from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils.database import get_problem_by_params, update_progress, get_solved_count
import json
from pathlib import Path

router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent
ACHIEVEMENTS_PATH = BASE_DIR / 'data' / 'achievements.json'

with open(ACHIEVEMENTS_PATH, encoding='utf-8') as f:
    ACHIEVEMENTS = json.load(f)


class Form(StatesGroup):
    choosing_exam = State()
    choosing_topic = State()
    solving_problem = State()


async def check_achievements(user_id: int, topic: str, solved_count: int, bot: Bot):
    if solved_count == 1:
        msg = ACHIEVEMENTS['first_problem']['description']
        await bot.send_message(user_id, msg)
    elif solved_count == 10:
        key = 'algebra_master' if topic == 'Алгебра' else 'geometry_master'
        msg = f"{ACHIEVEMENTS[key]['title']}\n{ACHIEVEMENTS[key]['description']}"
        await bot.send_message(user_id, msg)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(
        "📚 Выберите экзамен:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="ЕГЭ"), KeyboardButton(text="ОГЭ")]],
            resize_keyboard=True
        )
    )
    await state.set_state(Form.choosing_exam)


@router.message(Form.choosing_exam, F.text.in_(["ЕГЭ", "ОГЭ"]))
async def handle_exam(message: Message, state: FSMContext):
    await state.update_data(exam=message.text)
    await message.answer(
        "📚 Выберите тему:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Алгебра"), KeyboardButton(text="Геометрия")]],
            resize_keyboard=True
        )
    )
    await state.set_state(Form.choosing_topic)


@router.message(Form.choosing_topic, F.text.in_(["Алгебра", "Геометрия"]))
async def handle_topic(message: Message, state: FSMContext):
    user_data = await state.get_data()
    problem = await get_problem_by_params(user_data["exam"], message.text)

    if problem:
        await state.update_data(problem=problem, topic=message.text)
        await message.answer(
            f"📝 Задача ({user_data['exam']}, {message.text}):\n{problem['question']}",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.solving_problem)
    else:
        await message.answer("😔 Задачи закончились!")
        await state.clear()


@router.message(Form.solving_problem)
async def check_answer(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    problem = user_data["problem"]

    if message.text.strip() == problem["answer"]:
        await message.answer("✅ Правильно!")
        await update_progress(message.from_user.id, user_data["topic"])
        solved_count = await get_solved_count(message.from_user.id, user_data["topic"])
        await check_achievements(message.from_user.id, user_data["topic"], solved_count, bot)
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {problem['answer']}")

    await message.answer(f"📚 Объяснение:\n{problem['solution']}")

    new_problem = await get_problem_by_params(user_data["exam"], user_data["topic"])
    if new_problem:
        await state.update_data(problem=new_problem)
        await message.answer(f"📝 Новая задача ({user_data['exam']}, {user_data['topic']}):\n{new_problem['question']}")
    else:
        await message.answer("🎉 Вы решили все доступные задачи по этой теме!")
        await state.clear()