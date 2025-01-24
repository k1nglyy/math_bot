from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.database import get_random_problem

router = Router()

# Клавиатуры
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎓 Выбрать экзамен"), KeyboardButton(text="📚 Получить задачу")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True
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
    await message.answer(f"✅ Выбран {data['exam_type']} ({level}).\nНажмите '📚 Получить задачу'!",
                         reply_markup=main_menu)
    await state.set_state(UserState.solving_task)


@router.message(lambda message: message.text == "📚 Получить задачу", UserState.solving_task)
async def send_task(message: types.Message, state: FSMContext):
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


@router.message(UserState.solving_task)
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    problem = data.get('current_problem')
    if not problem:
        await message.answer("Сначала запросите задачу через меню!")
        return
    user_answer = message.text.strip().replace(",", ".").lower()
    correct_answers = [problem['answer'].replace(",", ".").lower()]
    if "/" in correct_answers[0] or "." in correct_answers[0]:
        try:
            decimal_value = float(correct_answers[0])
            rounded = round(decimal_value, 2)
            correct_answers.append(
                f"{rounded:.2f}".rstrip('0').rstrip('.') if rounded != int(rounded) else str(int(rounded)))
        except:
            pass
    if user_answer in correct_answers:
        await message.answer("✅ *Верно!* Молодец! 😊", parse_mode="Markdown")
    else:
        hint_text = (
            f"❌ *Неверно.* Правильный ответ: `{problem['answer']}`\n\n"
            f"{problem['hint']}"
        )
        if "дробь" in problem['hint']:
            hint_text += "\n\nℹ️ *Совет:* Если ответ — бесконечная дробь, округлите его до двух знаков или введите обыкновенной дробью (например, 1/3)."
        await message.answer(hint_text, parse_mode="Markdown")
    await send_task(message, state)