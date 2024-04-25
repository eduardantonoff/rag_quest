import os, requests, json
from pydantic import BaseModel, parse_obj_as
from typing import List, Dict

TOKEN = os.getenv('GPN_CHATBOT_TOKEN')
URL = os.getenv('GPN_API_URL')

WELCOME_MESSAGE = """Здравствуйте! 
Я виртуальный ассистент. 
Помогу ответить на ваши вопросы."""

FEEDBACK_MESSAGE = "Пожалуйста, оцените качество ответа виртуального ассистента!"

ERROR_MESSAGE = "Что-то пошло не так..."

TEMPLATE = """*ИЗВЛЕЧЁННЫЕ ВОПРОСЫ* ❓:

{question}

==========

*ПОДХОДЯЩИЕ ЧАНКИ ТЕКТА ИЗ БАЗЫ ЗНАНИЙ* 📚:

{meta}

==========

*ФИНАЛЬНЫЙ ОТВЕТ* 📩:

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

# def query_docs(body, template_id=1) -> ComplexQueryAnswerResponse:
    
#     url = f"{URL}/api/docs/query/{template_id}"
#     headers = {"Content-Type": "text/plain"}
    
#     response = requests.post(url, data=body, headers=headers)
#     if response.status_code == 200:
#         # Parse the response JSON into a ComplexQueryAnswerResponse object
#         return ComplexQueryAnswerResponse.parse_obj(response.json())
#     else:
#         return {"error": f"Failed with status code {response.status_code}"}
    
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

# def find_doc_provisions(body) -> StringListResponse:
#     url = f"{URL}/api/docs/provisions"
#     headers = {"Content-Type": "text/plain"}
    
#     response = requests.post(url, data=body, headers=headers)
#     if response.status_code == 200:
#         # Parse the response JSON into a StringListResponse object
#         return StringListResponse.parse_obj(response.json())
#     else:
#         return {"error": f"Failed with status code {response.status_code}"}

def convert_to_utf8(text):
    try:
        text.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        text = text.encode('latin1').decode('utf-8')
    
    return text

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


if __name__ == "__main__":
    query = '''
    Уважаемые коллеги,
    
    Добрый день! У меня возник вопрос относительно расчета начальной максимальной цены (НМЦ) при организации конкурентной процедуры и с рамочным договоров.
    
    Интересует, допустимо ли при расчете НМЦ указывать ориентировочный объем, умноженный на единичные расценки? Например, если планируется заключение рамочного договора на поставку товаров или оказание услуг с указанием ориентировочного объема, можно ли использовать стоимость какого-либо предполагаемого количества единиц товара или услуги, умноженную на соответствующую единичную расценку, для определения НМЦ?
    
    Буду благодарен за ваше профессиональное мнение и рекомендации по данному вопросу. Это важно для нас в контексте правильного и эффективного планирования закупочных процессов.
    
    С уважением,
    
    [Ваше Имя]
    [Ваша Должность]
    [Ваша Компания]
    '''

    print("getting asnwer....")
    answer = query_docs(1, query)
    print(answer)
    print("=======================================================")
    
    print("getting provisions....")
    provisions = find_doc_provisions("1.1")
    print(provisions)
    print("=======================================================")