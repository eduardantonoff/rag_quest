import asyncio, os, requests
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import dp, bot
from keyboards import choose_mode_kb, get_docs_kb, feedback_kb
from utils import WELCOME_MESSAGE, FEEDBACK_MESSAGE, ERROR_MESSAGE, query_docs_async

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
    print("1")
    args = message.get_args().split(maxsplit=0)
    print("2")
    template_id, body = 1, args[0].strip('\'"')
    print("3")
    try:
        print("4")
        template_id = int(template_id)
        print("5")
        await bot.send_message(
            chat_id=message.from_user.id, 
            text="Ваш запрос уже обрабатывается!\nПожалуйста, подождите около 30 секунд...", 
            reply_markup=get_docs_kb
        )
        print("6")
        result = await query_docs_async(template_id, body)
        await message.reply(f"Detected questions in your request: {result.question}")
        await message.reply(f"Answer: {result.answer}")
        await message.reply(f"Doc provisions related:")
        for provision in result.provisions:
            await message.reply(f"{provision.content}")
            
    except ValueError:
        await message.reply("Template ID must be an integer.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}") 
    
    # model_response = "<model response from api>" # model.get_response(inquery)
    
    # await bot.send_message(
    #     chat_id=message.from_user.id, 
    #     text=model_response, 
    #     reply_markup=get_docs_kb
    # )
    
    # await bot.send_message(
    #     chat_id=message.from_user.id, 
    #     text=FEEDBACK_MESSAGE, 
    #     reply_markup=feedback_kb
    # )
    
async def send_links(callback_query: types.CallbackQuery):
    
    # docs = "<docs form api>"
    # if type(content) == str:
    #     await bot.send_message(
    #         chat_id=callback_query.from_user.id, 
    #         text=content
    #     )
    # else:
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

# async def process_feedback(callback_query: types.CallbackQuery):
    
#     thanks_message = await bot.send_message(
#         chat_id=callback_query.from_user.id, 
#         text="Спасибо за отзыв!"
#     )
        
#     # Delete the message with the inline keyboard
#     await bot.delete_message(
#         chat_id=callback_query.message.chat.id, 
#         message_id=callback_query.message.message_id
#     ) 
    
#     # Delay before editing the message
#     await asyncio.sleep(2)
    
#     # Replace the message with a deleting animation
#     await bot.edit_message_text(
#         chat_id=callback_query.from_user.id, 
#         message_id=thanks_message.message_id,
#         text="Введите новый запрос:"
#     )


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
        # process_feedback, 
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