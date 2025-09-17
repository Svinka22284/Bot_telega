from aiogram import Bot,Dispatcher,executor,types
from dotenv import load_dotenv
from module1 import conn,cursor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup,InlineKeyboardMarkup
import os
from aiogram.dispatcher import FSMContext
import pyodbc
class TaskState(StatesGroup):
    waiting_for_task_number = State()
load_dotenv("TextFile1.env")
bot=Bot(os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


main = types.ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Завдання').add('Мои завдання')

main_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('Завдання').add('Мои завдання').add('Админ панель')


main_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_panel.add('Добавить Завдання').add('Удалить завдання').add('Изменить задание').add('Просмотр пользователей')
catalog_list=InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='Взять задание',callback_data="take_task"),InlineKeyboardButton(text='Подробности о задании', callback_data="info_task"))

@dp.message_handler(commands=['start'])
async def cmd_start(message:types.Message):
    await cmd_start_db(message.from_user.id,message.from_user.first_name)
    await message.answer(
        f"{message.from_user.first_name}, вітаю вас у нашому боті для завдань!",
        reply_markup=main
    )
    if message.from_user.id==int(os.getenv('IDADMIN')):
        await message.answer(
            f'Вы авторизовались как администратор!',reply_markup=main_admin
            )

@dp.callback_query_handler(lambda c: c.data == "take_task")
async def choose_task(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, "Введите номер задания:")
    await TaskState.waiting_for_task_number.set()
@dp.message_handler(state=TaskState.waiting_for_task_number)
async def get_task(message: types.Message, state: FSMContext):
   try:
        task_id = int(message.text)
        

        
        cursor.execute(
              "INSERT INTO Myexercise (name1) VALUES (?)",
                (message.from_user.first_name)
            )
        conn.commit()

        await message.answer("взято")
        
        await message.answer("Задание с таким номером не найдено.")

   except ValueError:
        await message.answer("Введите корректный номер (число).")

   await state.finish()

@dp.callback_query_handler(lambda c: c.data == "info_task")
async def info_task(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, "Введите номер задания:")
    await TaskState.waiting_for_task_number.set()
@dp.message_handler(state=TaskState.waiting_for_task_number)
async def get_task(message: types.Message, state: FSMContext):
    try:
        task_id = int(message.text)

        cursor = conn.cursor()
        cursor.execute("SELECT name1, description1 FROM Myexercise WHERE id_Myexercise = ?", (task_id,))
        row = cursor.fetchone()

        if row:
            await message.answer(f"Задание №{task_id}\nНазвание: {row[0]}\nОписание: {row[1]}")
        else:
            await message.answer("Задание с таким номером не найдено.")

    except ValueError:
        await message.answer("Введите корректный номер (число).")

    await state.finish()

@dp.message_handler(commands=['id'])
async def cmd_start(message:types.Message):
    await message.answer(f'{message.from_user.id}')

@dp.message_handler(text='Завдання')
async def cart(message:types.Message):
   cursor.execute("SELECT * FROM exercise")
   rows = cursor.fetchall()
   if rows:    
        text = "\n".join([str(row) for row in rows])
   else:
        text = "У таблиці exercis поки що немає даних."
  
   await message.answer(text,reply_markup=catalog_list)


@dp.message_handler(text='Админ панель')
async def Admin(message:types.Message):
    await message.answer(f'администратор!',reply_markup=main_panel)


@dp.message_handler(text='Мои завдання')
async def  my_tasks(message:types.Message):
   cursor.execute("SELECT * FROM Myexercise")
   rows = cursor.fetchall()
   if rows:    
        text = "\n".join([str(row) for row in rows])
   else:
        text = "У таблиці exercis поки що немає даних."
   await message.answer(text)

@dp.message_handler(text='Просмотр пользователей')
async def view_users(message:types.Message):
   cursor.execute("SELECT * FROM Excutor")
   rows = cursor.fetchall()
   if rows:    
        text = "\n".join([str(row) for row in rows])
   else:
        text = "У таблиці exercis поки що немає даних."
   await message.answer(text)



async def cmd_start_db(user_id,first_name):
    cursor.execute("SELECT * FROM Excutor WHERE id_tg = ?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute("INSERT INTO Excutor (id_tg,Name2) VALUES (?,?)", (user_id, first_name))
        conn.commit()
      
        
@dp.message_handler(lambda message: True, state=None)
async def answer(message:types.Message):
    await message.reply('Не розумію')


if __name__=='__main__':
    executor.start_polling(dp)