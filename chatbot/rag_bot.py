import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import executor
import os

feedback_score = []

WELCOME_MESSAGE =  """Здравствуйте! 
Я виртуальный ассистент. 
Помогу ответить на ваши вопросы."""

welcome_text = WELCOME_MESSAGE

# Initialize bot and dispatcher
API_TOKEN = os.getenv('GPN_CHATBOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Function for model response
async def get_model_response(message):
    # Perform some preprocessing on the user's message
    # processed_message = 

    # Placeholder for actual model response
    model_response = "SOME MODEL RESPONSE" #+ processed_message

    return model_response

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(f'{WELCOME_MESSAGE}')
    await message.answer("Введите ваш запрос:")
    
async def get_feedback_field(id):
    # Additional message with inline keyboard
    feedback_keyboard = types.InlineKeyboardMarkup()
    feedback_keyboard.add(
        types.InlineKeyboardButton(text='👍', callback_data='1'),
        types.InlineKeyboardButton(text='👎', callback_data='0')
    )
    
    feedback_message = await bot.send_message(
        id, "Пожалуйста, оцените качество ответа виртуального ассистента!",
        reply_markup=feedback_keyboard
    )
    return feedback_message
    

# Handler for user messages
@dp.message_handler()
async def echo(message: types.Message):
    
    global feedback_message
    
    links_keyboard = types.InlineKeyboardMarkup()
    links_keyboard.add(
        types.InlineKeyboardButton(
            text='Ссылки на нормативные документы', 
            callback_data='docs_links')
    )
    
    model_response = await get_model_response(message)
    sent_message = await message.answer(model_response, reply_markup=links_keyboard)
    
    await get_feedback_field(message.chat.id)
    return sent_message

@dp.callback_query_handler(lambda query: query.data == 'docs_links')
async def send_links(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Ответ основан на следующих пунктах документации:")
    for i in range(3):
        await bot.send_message(callback_query.from_user.id, f"Link {i+1}")
    
# Handler for inline keyboard feedback
@dp.callback_query_handler(lambda query: query.data in ['0', '1'])
async def process_feedback(callback_query: types.CallbackQuery):
    
    global feedback_score
    feedback_score.append(callback_query.data)
    thanks_message = await bot.send_message(callback_query.from_user.id, "Спасибо за отзыв!")
        
    # Delete the message with the inline keyboard
    await bot.delete_message(
        chat_id=callback_query.message.chat.id, 
        message_id=callback_query.message.message_id
    ) 
    
    # Delay before editing the message
    await asyncio.sleep(2)
    
    # Replace the message with a deleting animation
    await bot.edit_message_text(
        "Введите новый запрос:", 
        chat_id=callback_query.from_user.id, 
        message_id=thanks_message.message_id
    )

# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)