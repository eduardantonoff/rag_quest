import asyncio, os, requests
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import dp, bot
from keyboards import choose_mode_kb, get_docs_kb, feedback_kb
from utils import WELCOME_MESSAGE, FEEDBACK_MESSAGE, \
      get_model_response_from_api, get_docs_from_api

content = (None,)

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

async def set_model_mode(message: types.Message, state: FSMContext):
    await ModeStates.model_mode.set()
    await bot.send_message(
        chat_id=message.from_user.id, 
        text="Введите ваш запрос:"
    ) 
    
    
async def get_model_response(message: types.Message, state: FSMContext):
    global content
    
    try:   
        await bot.send_message(
            chat_id=message.from_user.id, 
            text="Ваш запрос уже обрабатывается!\nПожалуйста, подождите около 30 секунд..." 
        )
        
        model_response, content = await get_model_response_from_api(message.text)
        
        await bot.send_message(
            chat_id=message.from_user.id, 
            text=model_response, 
            reply_markup=get_docs_kb
        )
            
    except Exception as e:
        await bot.send_message(
            chat_id=message.from_user.id, 
            text=f"An error occurred: {str(e)}", 
            reply_markup=get_docs_kb
        )
        
    
async def send_links(callback_query: types.CallbackQuery):
    
    for doc in content:
        await bot.send_message(
            chat_id=callback_query.from_user.id, 
            text=doc
        )

# ======================== DATABASE HANDLERS ========================

async def set_database_mode(message: types.Message, state: FSMContext):
    await ModeStates.database_mode.set()
    await bot.send_message(
        chat_id=message.from_user.id, 
        text="Введите ваш запрос:"
    )
    
async def get_database_response(message: types.Message, state: FSMContext):    
    
    try:
        database_response = await get_docs_from_api(message.text)
        
        for doc in database_response:
            await bot.send_message(
                chat_id=message.from_user.id, 
                text=doc
            )
        
    except Exception as e:
        await bot.send_message(
            chat_id=message.from_user.id, 
            text=f"An error occurred: {str(e)}"
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
    
    dp.register_message_handler(
        get_model_response, 
        state=ModeStates.model_mode
    )
    
    dp.register_message_handler(
        get_database_response, 
        state=ModeStates.database_mode
    )