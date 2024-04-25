import os, requests, aiohttp
from pydantic import BaseModel, parse_obj_as
from typing import List, Dict, Tuple

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

ПОДХОДЯЩИЕ ПУНКТЫ ИЗ БАЗЫ ЗНАНИЙ 📚:

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
    
    
async def query_docs_async(body, template_id=1) -> ComplexQueryAnswerResponse:
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
            

async def find_doc_provisions(body) -> StringListResponse:
    url = f"{URL}/api/docs/provisions"
    headers = {"Content-Type": "text/plain"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body, headers=headers) as response:
            
            if response.status == 200:
                resp_json = await response.json()
                return StringListResponse.parse_obj(response)
            else:
                raise Exception(f"Failed with status code {response.status}")


def parse_provisions(provisions: DocumentProvisionReference) -> Tuple[str, Tuple]:
    contents = set()
    metas = set()
    
    for i in provisions:
        meta = ", ".join(i.meta.values())
        content_text = i.content
        content = ":\n".join([meta, content_text])
        metas.update([meta])
        contents.update([content])
        
    meta = "\n".join(metas)
    return meta, tuple(contents)
          

def parse_model_response(response: ComplexQueryAnswerResponse) -> Tuple[str, Tuple]:
    
    question = response.question
    answer = response.answer
    provisions = response.provisions
    
    meta, contents = parse_provisions(provisions)
    model_answer = TEMPLATE.format(question=question, meta=meta, answer=answer)
    
    return model_answer, tuple(contents)


async def get_model_response_from_api(text: str) -> Tuple[str, Tuple]:
    body = text.strip('\'"')
    response = await query_docs_async(body)
    return parse_model_response(response)