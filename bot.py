import os
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
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# --- Машина состояний ---
class AddRecord(StatesGroup):
    amount = State()
    comment = State()

# --- Старт ---
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("➕ Добавить запись")
    await message.answer("Добро пожаловать! Выберите команду:", reply_markup=keyboard)

# --- Добавление записи ---
@dp.message_handler(lambda m: m.text == "➕ Добавить запись")
async def cmd_add(message: types.Message):
    user_id = message.from_user.id
    if user_id not in MANAGER_MAP:
        await message.answer("Вам недоступна эта команда.")
        return
    await message.answer("Введите сумму (отрицательное число = расход):")
    await AddRecord.amount.set()

@dp.message_handler(state=AddRecord.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount > 0:
            amount = -abs(amount)
        await state.update_data(amount=amount)
        await message.answer("Введите комментарий:")
        await AddRecord.comment.set()
    except ValueError:
        await message.answer("Некорректная сумма. Попробуйте ещё раз.")

@dp.message_handler(state=AddRecord.comment)
async def process_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text
    user_id = message.from_user.id
    manager_name = MANAGER_MAP.get(user_id, str(user_id))
    sheets.append_record(manager_name, datetime.now(), data["amount"], comment)
    await message.answer("Запись добавлена ✅")
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
