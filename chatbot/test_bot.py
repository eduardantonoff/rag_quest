import requests
from pydantic import BaseModel, parse_obj_as
from typing import List, Dict


class DocumentProvisionReference(BaseModel):
    content: str
    meta: Dict[str, str]


class ComplexQueryAnswerResponse(BaseModel):
    question: str
    answer: str
    sources: str
    provisions: List[DocumentProvisionReference]


class StringListResponse(BaseModel):
    response: List[str]


def query_docs(template_id, body) -> ComplexQueryAnswerResponse:
    url = f"http://localhost:8000/api/docs/query/{template_id}"
    headers = {"Content-Type": "text/plain"}
    response = requests.post(url, data=body, headers=headers)
    if response.status_code == 200:
        # Parse the response JSON into a ComplexQueryAnswerResponse object
        return ComplexQueryAnswerResponse.parse_obj(response.json())
    else:
        return {"error": f"Failed with status code {response.status_code}"}


def find_doc_provisions(body) -> StringListResponse:
    url = "http://localhost:8000/api/docs/provisions"
    headers = {"Content-Type": "text/plain"}
    response = requests.post(url, data=body, headers=headers)
    if response.status_code == 200:
        # Parse the response JSON into a StringListResponse object
        return StringListResponse.parse_obj(response.json())
    else:
        return {"error": f"Failed with status code {response.status_code}"}


import logging
import aiohttp
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

load_dotenv()
API_TOKEN = os.getenv("GPN_CHATBOT_TOKEN") #'YOUR_TELEGRAM_BOT_API_TOKEN'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def query_docs_async(template_id, body) -> ComplexQueryAnswerResponse:
    # Assuming `query_docs` is your API call function (make sure to adjust the implementation for async HTTP calls)
    url = f"http://localhost:8000/api/docs/query/{template_id}"
    headers = {"Content-Type": "text/plain"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body, headers=headers) as response:
            if response.status == 200:
                resp_json = await response.json()
                return ComplexQueryAnswerResponse.parse_obj(resp_json)
            else:
                raise Exception(f"Failed with status code {response.status}")

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm your bot to query documents. Use /query <template_id> <query_text> to get started.")

@dp.message_handler(commands=['query'])
async def handle_query(message: types.Message):
    args = message.get_args().split(maxsplit=0)
    if len(args) != 1:
        await message.reply("Please use the format: /query <query_text>")
        return

    template_id, body = 1, args[0].strip('\'"')
    try:
        template_id = int(template_id)
        await message.reply(f"Processing your request, pls wait for 30 secs or so...")
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

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
    
    
# if __name__ == "__main__":
    # query = '''
    # Уважаемые коллеги,
    
    # Добрый день! У меня возник вопрос относительно расчета начальной максимальной цены (НМЦ) при организации конкурентной процедуры и с рамочным договоров.
    
    # Интересует, допустимо ли при расчете НМЦ указывать ориентировочный объем, умноженный на единичные расценки? Например, если планируется заключение рамочного договора на поставку товаров или оказание услуг с указанием ориентировочного объема, можно ли использовать стоимость какого-либо предполагаемого количества единиц товара или услуги, умноженную на соответствующую единичную расценку, для определения НМЦ?
    
    # Буду благодарен за ваше профессиональное мнение и рекомендации по данному вопросу. Это важно для нас в контексте правильного и эффективного планирования закупочных процессов.
    
    # С уважением,
    
    # [Ваше Имя]
    # [Ваша Должность]
    # [Ваша Компания]
    # '''

    # print("getting asnwer....")
    # answer = query_docs(1, query)
    # print(answer)
    # print("=======================================================")
    
    # print("getting provisions....")
    # provisions = find_doc_provisions("1.1")
    # print(provisions)
    # print("=======================================================")
