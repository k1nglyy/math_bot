from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Получить задачу")],
        [KeyboardButton(text="🎓 Выбрать экзамен")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🏆 Достижения")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

exam_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ЕГЭ")],
        [KeyboardButton(text="ОГЭ")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите экзамен"
)

level_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="база")],
        [KeyboardButton(text="профиль")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите уровень"
)