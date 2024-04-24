from aiogram.utils import executor
from create_bot import dp
from handlers import register_handlers

async def on_startup(_):
    print('ALL UPDATES IS SUCSESSFULL\nBOT IS ONLINE')

register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)