import asyncio
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
import os
import db
from eljur import is_valid, get_new_marks

token = os.getenv("ELJUR_BOT_TOKEN")
bot = Bot(token=token)
dp = Dispatcher()

tasks = {}


class LoginStates(StatesGroup):
    login = State()
    password = State()


class TimeStates(StatesGroup):
    time = State()


async def send_new_marks(user_id, login, password, check=False):
    if not is_valid(login, password):
        await bot.send_message(user_id, "Данные логин и пароль недействительны. "
                                        "Проверка новых оценок остановлена. "
                                        "Чтобы еще раз авторизоваться введите команду /login")
        db.delete_user(user_id)
        tasks[user_id].cancel()
        del tasks[user_id]
    else:
        new_marks = get_new_marks(user_id)
        if new_marks:
            await bot.send_message(user_id, "❗️Появились новые оценки❗️")
            for subject, marks in new_marks.items():
                text = f"{subject}\n"
                for (mark, (day, month)) in marks:
                    if '-' in mark:
                        mark = mark.replace('-', '\-')
                    text += f"*{mark}* за {day:02}\.{month:02}\n"
                await bot.send_message(user_id, text, parse_mode="MarkdownV2")
        else:
            if check:
                await bot.send_message(user_id, "Новых оценок пока нет❌")


async def new_marks_task(user_id, login, password, time):
    while True:
        await send_new_marks(user_id, login, password)
        await asyncio.sleep(time)


@dp.message(F.text, Command("time"), StateFilter(None))
async def time_command(message: types.Message, state: FSMContext):
    await message.answer(f"Текущий интервал \- *{db.get_time(message.chat.id) // 60}* минут\. "
                         f"Чтобы изменить его введите целое количество минут не меньше *5* и не больше *1440*",
                         parse_mode="MarkdownV2")
    await state.set_state(TimeStates.time)


@dp.message(F.text, Command("check"), StateFilter(None))
async def check_command(message: types.Message, state: FSMContext):
    if message.chat.id not in db.get_users():
        await message.answer("Для проверки новых оценок необходимо авторизоваться. "
                             "Для этого введите команду /login")
    else:
        await send_new_marks(message.chat.id, *db.get_authorization(message.chat.id), check=True)


@dp.message(F.text.as_("time"), TimeStates.time)
async def get_time(message: types.Message, state: FSMContext, time: str):
    if time.isdecimal() and 5 <= int(time) <= 1440:
        db.set_time(message.chat.id, int(time) * 60)
        await message.answer(f"Интервал успешно изменён на *{time}* минут✅", parse_mode="MarkdownV2")
        if message.chat.id in tasks:
            tasks[message.chat.id].cancel()
            tasks[message.chat.id] = asyncio.create_task(
                new_marks_task(message.chat.id,
                               *db.get_authorization(message.chat.id),
                               db.get_time(message.chat.id))
            )
    else:
        await message.answer("Неверный формат ввода интервала❌")
    await state.clear()


@dp.message(F.text, Command("start"), StateFilter(None))
async def start_command(message: types.Message):
    name = message.chat.first_name
    await message.answer(text=f"Здравствуй, {name}! Я помогу тебе следить за твоими оценками.\n\n"
                              f"Ты можешь отправлять мне следующие команды:\n\n"
                              f"/login - авторизоваться на сайте\n"
                              f"/time - изменить интервал проверки оценок\n"
                              f"/check - проверить новые оценки в данный момент")


@dp.message(F.text, Command("login"), StateFilter(None))
async def login_command(message: types.Message, state: FSMContext):
    await message.answer("Чтобы авторизоваться,  введите свой логин")
    await state.set_state(LoginStates.login)


@dp.message(F.text.as_("login"), LoginStates.login)
async def get_login(message: types.Message, state: FSMContext, login):
    await state.update_data(login=login)
    await message.answer("Логин получен, теперь введите пароль")
    await state.set_state(LoginStates.password)


@dp.message(F.text.as_("password"), LoginStates.password)
async def get_password(message: types.Message, state: FSMContext, password):
    data = await state.get_data()
    login = data["login"]
    await message.answer("Идёт проверка данных...")
    if is_valid(login, password):
        db.add_user(message.chat.id, login, password)
        time = db.get_time(message.chat.id)
        await message.answer(f"Вы успешно авторизовались✅. "
                             f"Проверка новых оценок будет происходить каждые {time // 60} минут.\n"
                             "Если хотите изменить это время, введите команду /time")
        if message.chat.id in tasks:
            tasks[message.chat.id].cancel()
        tasks[message.chat.id] = asyncio.create_task(new_marks_task(message.chat.id, login, password, time))
    else:
        await message.answer("Неверный логин или пароль❌")
    await state.clear()


def start_bot():
    for user_id in db.get_users():
        tasks[user_id] = asyncio.create_task(
            new_marks_task(user_id, *db.get_authorization(user_id), db.get_time(user_id))
        )


async def main():
    start_bot()
    await dp.start_polling(bot, skip_updates=False)
