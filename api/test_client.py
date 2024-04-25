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
