import asyncio, os, requests
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import dp, bot
from keyboards import choose_mode_kb, get_docs_kb, feedback_kb
from utils import WELCOME_MESSAGE, FEEDBACK_MESSAGE, URL

class ModeStates(StatesGroup):
    model_mode = State()
    database_mode = State()

async def start_chat(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=WELCOME_MESSAGE, 
        reply_markup=choose_mode_kb
    )
    await message.delete()

# ======================== MODEL HANDLERS ========================

# Уважаемые коллеги,  Добрый день! У меня возник вопрос относительно расчета начальной максимальной цены (НМЦ) при организации конкурентной процедуры и с рамочным договоров.  Интересует, допустимо ли при расчете НМЦ указывать ориентировочный объем, умноженный на единичные расценки? Например, если планируется заключение рамочного договора на поставку товаров или оказание услуг с указанием ориентировочного объема, можно ли использовать стоимость какого-либо предполагаемого количества единиц товара или услуги, умноженную на соответствующую единичную расценку, для определения НМЦ?  Буду благодарен за ваше профессиональное мнение и рекомендации по данному вопросу. Это важно для нас в контексте правильного и эффективного планирования закупочных процессов.  С уважением,  [Ваше Имя] [Ваша Должность] [Ваша Компания]

async def set_model_mode(message: types.Message, state: FSMContext):
    await ModeStates.model_mode.set()
    await bot.send_message(
        chat_id=message.from_user.id, 
        text="Введите ваш запрос:"
    )
    
async def get_model_response(message: types.Message, state: FSMContext):
    full_url = URL + "/api/docs/query/{template_id}"
    body = str(message.text)
    headers = {'Content-Type': 'text/plain'}
    
    response = requests.post(full_url.format(template_id=1), headers=headers, data=body)
    print(response.elapsed.total_seconds())
    print(response.status_code, response.json(), sep='\n')
    
    model_response = "<model response from api>" # model.get_response(inquery)
    
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=model_response, 
        reply_markup=get_docs_kb
    )
    
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=FEEDBACK_MESSAGE, 
        reply_markup=feedback_kb
    )
    
async def send_links(callback_query: types.CallbackQuery):
    
    docs = "<docs form api>"
    
    await bot.send_message(
        chat_id=callback_query.from_user.id, 
        text=docs
    )
    
# ======================== DATABASE HANDLERS ========================

async def set_database_mode(message: types.Message, state: FSMContext):
    await ModeStates.database_mode.set()
    await bot.send_message(
        chat_id=message.from_user.id, 
        text="Введите ваш запрос:"
    )
    
async def get_database_response(message: types.Message, state: FSMContext):
    inquery = message.text
    
    response = requests.post(URL + "/api/query/2", data=inquery)
    print(response)
    
    database_response = "<database response from api>" #model.get_response(inquery)
    
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=database_response
    )
    
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=FEEDBACK_MESSAGE, 
        reply_markup=feedback_kb
    )

# ======================== FEEDBACK HANDLERS ========================

async def process_feedback(callback_query: types.CallbackQuery):
    
    thanks_message = await bot.send_message(
        chat_id=callback_query.from_user.id, 
        text="Спасибо за отзыв!"
    )
        
    # Delete the message with the inline keyboard
    await bot.delete_message(
        chat_id=callback_query.message.chat.id, 
        message_id=callback_query.message.message_id
    ) 
    
    # Delay before editing the message
    await asyncio.sleep(2)
    
    # Replace the message with a deleting animation
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id, 
        message_id=thanks_message.message_id,
        text="Введите новый запрос:"
    )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_chat, 
        commands=["start", "help"]
    )

    dp.register_message_handler(
        set_model_mode, 
        Text(equals="задать вопрос ❓️", ignore_case=True), 
        state='*'
    )
    
    dp.register_message_handler(
        set_database_mode, 
        Text(equals="найти пункт документации 📄", ignore_case=True), 
        state='*'
    )
    
    dp.register_callback_query_handler(
        send_links, 
        lambda callback: callback.data == "get_docs",
        state=ModeStates.model_mode
    )
    
    dp.register_callback_query_handler(
        process_feedback, 
        lambda callback: callback.data in ["like", "dislike"],
        state='*'
    )
    
    dp.register_message_handler(
        get_model_response, 
        state=ModeStates.model_mode
    )
    
    dp.register_message_handler(
        get_database_response, 
        state=ModeStates.database_mode
    )