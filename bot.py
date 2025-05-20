import os
API_TOKEN = "908109651:AAGi26LN4zvmyplWNx9wCiO9U0yMqZYHUL0"

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from datetime import datetime
import logging

import sheets
from roles import MANAGER_MAP


API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class AddRecord(StatesGroup):
    amount = State()
    comment = State()

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    types.KeyboardButton("Добавить запись"),
    types.KeyboardButton("Посмотреть баланс")
)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот учёта. Выберите действие:", reply_markup=main_menu)

@dp.message_handler(lambda msg: msg.text == "Добавить запись")
async def add_start(message: types.Message):
    await message.answer("Введите сумму (например: 1500 или -700):", reply_markup=types.ReplyKeyboardRemove())
    await AddRecord.amount.set()

@dp.message_handler(state=AddRecord.amount)
async def get_amount(message: types.Message, state: FSMContext):
    raw = message.text.strip().replace(",", ".")
    if not raw.startswith(("+", "-")):
        raw = "-" + raw
    try:
        amount = float(raw)
        await state.update_data(amount=amount)
        await message.answer("Введите комментарий:")
        await AddRecord.comment.set()
    except ValueError:
        await message.answer("Некорректная сумма. Введите число.")

@dp.message_handler(state=AddRecord.comment)
async def get_comment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    comment = message.text
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    user_id = message.from_user.id
    manager_name = MANAGER_MAP.get(user_id, f"unknown_{user_id}")
    row = [str(user_id), now, user_data['amount'], comment]

    try:
        sheets.append_to_named_sheet(manager_name, row)
        await message.answer(f"Запись добавлена в лист: {manager_name}.", reply_markup=main_menu)
    except Exception as e:
        await message.answer(f"Ошибка при записи: {e}", reply_markup=main_menu)

    await state.finish()

@dp.message_handler(lambda msg: msg.text == "Посмотреть баланс")
async def show_balance(message: types.Message):
    user_id = message.from_user.id
    manager_name = MANAGER_MAP.get(user_id, f"unknown_{user_id}")
    try:
        balance = sheets.get_balance(manager_name)
        await message.answer(f"Ваш текущий баланс: {balance:.2f} ₽", reply_markup=main_menu)
    except Exception as e:
        await message.answer(f"Ошибка при получении баланса: {e}", reply_markup=main_menu)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
