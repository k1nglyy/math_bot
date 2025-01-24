from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.database import get_random_problem

router = Router()


class UserState(StatesGroup):
    choosing_exam = State()
    choosing_level = State()
    solving_task = State()


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я MathExamBot. Выбери экзамен:\n"
        "/ege - ЕГЭ\n/oge - ОГЭ"
    )
    await state.set_state(UserState.choosing_exam)


@router.message(Command("ege"), UserState.choosing_exam)
async def set_ege(message: types.Message, state: FSMContext):
    await state.update_data(exam_type="ЕГЭ")
    await message.answer("Выбран ЕГЭ. Укажи уровень:\n/base - База\n/profile - Профиль")
    await state.set_state(UserState.choosing_level)


@router.message(Command("oge"), UserState.choosing_exam)
async def set_oge(message: types.Message, state: FSMContext):
    await state.update_data(exam_type="ОГЭ")
    await message.answer("Выбран ОГЭ. Уровень: база. Нажми /task")
    await state.set_state(UserState.solving_task)


@router.message(Command("base"), UserState.choosing_level)
async def set_base(message: types.Message, state: FSMContext):
    await state.update_data(level="база")
    data = await state.get_data()
    await message.answer(f"Экзамен: {data['exam_type']}, уровень: база. /task")
    await state.set_state(UserState.solving_task)


@router.message(Command("profile"), UserState.choosing_level)
async def set_profile(message: types.Message, state: FSMContext):
    await state.update_data(level="профиль")
    data = await state.get_data()
    await message.answer(f"Экзамен: {data['exam_type']}, уровень: профиль. /task")
    await state.set_state(UserState.solving_task)


@router.message(Command("task"), UserState.solving_task)
async def send_task(message: types.Message, state: FSMContext):
    data = await state.get_data()
    problem = get_random_problem(data['exam_type'], data.get('level', 'база'))

    if problem:
        await state.update_data(current_problem=problem)
        await message.answer(
            f"**{problem['topic']}**\n{problem['text']}\n\n"
            "Отправь ответ или нажми /hint"
        )
    else:
        await message.answer("😢 Задачи закончились")


@router.message(Command("hint"), UserState.solving_task)
async def send_hint(message: types.Message, state: FSMContext):
    data = await state.get_data()
    problem = data.get('current_problem')
    if problem:
        await message.answer(f"Подсказка: {problem['hint']}")
    else:
        await message.answer("Сначала запросите задачу /task")


@router.message(UserState.solving_task)
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    problem = data.get('current_problem')

    if not problem:
        await message.answer("Сначала запросите задачу /task")
        return

    if message.text.strip() == problem['answer']:
        await message.answer("✅ Верно! +10 баллов.")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {problem['answer']}")

    await send_task(message, state)