from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

choose_mode_kb = ReplyKeyboardMarkup(resize_keyboard=True)
model_button = KeyboardButton(text="Задать вопрос ❓️")
database_button = KeyboardButton(text="Найти пункт документации 📄")
choose_mode_kb.add(model_button).add(database_button)