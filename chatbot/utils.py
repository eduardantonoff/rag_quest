import os, requests, aiohttp
from pydantic import BaseModel, parse_obj_as
from typing import List, Dict

TOKEN = os.getenv('GPN_CHATBOT_TOKEN')
URL = os.getenv('GPN_API_URL')

WELCOME_MESSAGE = """Здравствуйте! 
Я виртуальный ассистент. 
Помогу ответить на ваши вопросы."""

FEEDBACK_MESSAGE = "Пожалуйста, оцените качество ответа виртуального ассистента!"

ERROR_MESSAGE = "Что-то пошло не так..."

TEMPLATE = """ИЗВЛЕЧЁННЫЕ ВОПРОСЫ ❓:

{question}

==========

ПОДХОДЯЩИЕ ЧАНКИ ТЕКТА ИЗ БАЗЫ ЗНАНИЙ 📚:

{meta}

==========

ФИНАЛЬНЫЙ ОТВЕТ 📩:

{answer}"""

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
    
    
async def query_docs_async(template_id, body) -> ComplexQueryAnswerResponse:
    # Assuming `query_docs` is your API call function (make sure to adjust the implementation for async HTTP calls)
    url = f"{URL}/api/docs/query/{template_id}"
    headers = {"Content-Type": "text/plain"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body, headers=headers) as response:
            if response.status == 200:
                resp_json = await response.json()
                return ComplexQueryAnswerResponse.parse_obj(resp_json)
            else:
                raise Exception(f"Failed with status code {response.status}")


def find_doc_provisions(body) -> StringListResponse:
    url = "http://localhost:8000/api/docs/provisions"
    headers = {"Content-Type": "text/plain"}
    response = requests.post(url, data=body, headers=headers)
    if response.status_code == 200:
        # Parse the response JSON into a StringListResponse object
        return StringListResponse.parse_obj(response.json())
    else:
        return {"error": f"Failed with status code {response.status_code}"}

# def find_doc_provisions(body) -> StringListResponse:
#     url = f"{URL}/api/docs/provisions"
#     headers = {"Content-Type": "text/plain"}
    
#     response = requests.post(url, data=body, headers=headers)
#     if response.status_code == 200:
#         # Parse the response JSON into a StringListResponse object
#         return StringListResponse.parse_obj(response.json())
#     else:
#         return {"error": f"Failed with status code {response.status_code}"}

def parse_model_response(response: dict) -> tuple:
    
    question = response["question"]
    answer = response["answer"]
    provisions = response["provisions"]

    contents = set()
    metas = set()
    
    for i in provisions:
        meta = ", ".join(i["meta"].values())
        content_text = i["content"]
        content = ":\n".join([meta, content_text])
        metas.update([meta])
        contents.update([content])
    
    meta = "\n".join(metas)
    model_answer = TEMPLATE.format(question=question, meta=meta, answer=answer)
    
    return model_answer, tuple(contents)


def get_model_response_from_api(text: str):
    
    url = f"{URL}/api/docs/query/1"
    headers = {'Content-type': 'text/plain'}
    
    response = requests.post(url, data=text, headers=headers)
    
    if response.status_code == 200:
        return parse_model_response(response.json())
    return (ERROR_MESSAGE, (ERROR_MESSAGE,))