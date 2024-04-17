# processing:
import os
import re
import pandas as pd
from dotenv import load_dotenv

# neo4j:
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector

# llm:
from langchain.chat_models.gigachat import GigaChat
from langchain_community.embeddings import GigaChatEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# retrieval:
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.memory import ConversationBufferMemory


class RAGModel():
    
    def __init__(self) -> None:
        # env
        load_dotenv("template.env")

        # neo4j:
        NEO4J_URI = os.getenv('NEO4J_URI')
        NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
        NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
        NEO4J_DATABASE= os.getenv('NEO4J_DATABASE')

        # llm:
        LLM_SCOPE = os.getenv('SCOPE')
        LLM_AUTH = os.getenv('AUTH_DATA')

        # llm initialization
        self.llm = GigaChat(
            credentials = LLM_AUTH, 
            temperature = 0.3, 
            n = 1, 
            model = "GigaChat-Plus", # 32k context window
            repetition_penalty = 1.0,
            verify_ssl_certs = False
        )

        # parser initialization
        self.parser = StrOutputParser()

        # embeddings initialization
        self.embeddings = GigaChatEmbeddings(
            credentials = LLM_AUTH, 
            verify_ssl_certs = False
        )

        # promt template
        self.template = """
                    Задача: Анализировать заданный запрос и предоставлять детализированные ответы, опираясь на документы, правила и требования.

                    Инструкции:

                    1. При ответе на вопросы, особенно те, которые связаны с правилами или нормативными документами, активно ссылайтесь на номера пунктов, статей и разделов документов.
                    2. Ваши ответы должны быть максимально точными и содержать не только ссылки на документы, но и объяснения их применения к данному запросу.

                    Вопрос: {question}
                    Контекст: {context}
                    
                    Ответ: Предоставьте ваш ответ, опираясь на указанные выше указания, отформотируйте текст под выдачу в телеграмм
                    """

        # prompt initialization
        self.prompt = ChatPromptTemplate.from_template(self.template)
        
        neo4j_vector = Neo4jVector.from_existing_index(
            self.embeddings,
            url = NEO4J_URI,
            username = NEO4J_USERNAME,
            password = NEO4J_PASSWORD,
            index_name = "vector"
            # search_type = 'hybrid'
        )
        
        # llm retrival chain
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm,
            chain_type = "stuff", # "stuff", "map_rerank", "refine"
            retriever = neo4j_vector.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=False,
            reduce_k_below_max_tokens=False,
            max_tokens_limit=32000,
            chain_type_kwargs = {
                "verbose": False,
                "prompt": self.prompt, # step_back_prompt
                "document_variable_name": "context",
                "memory": ConversationBufferMemory(
                    memory_key='history',
                    input_key='question'
                ),
            }
        )
        
        

    # sub query functions
    def step_back_prompt(self, text):
        
        chain = self.llm | self.parser

        template = f"""
                    Задача: Анализировать представленные данные и вывести из них высокоуровневые концепции и основные принципы.

                    Инструкции:
                    Прежде чем приступить к абстракции, важно:
                    1. Определить и выделить ключевые детали и специфику представленного материала.
                    2. Анализировать связи между деталями для понимания более глубоких закономерностей и взаимосвязей.
                    3. Структурировать полученные данные, выделяя общие элементы и паттерны.
                    4. Формулировать высокоуровневые концепции и принципы, опираясь на проанализированные данные.

                    Текст: \"{text}\"

                    Проанализируйте и сформулируйте общие концепции и основные принципы на основе представленных деталей в виде развернутых вопросов.
                    """

        model_response = chain.invoke(template)   
        return model_response


    def extract_question(self, text):
        
        chain = self.llm | self.parser

        template = f"""
                    Мне нужно твоё содействие в анализе следующего делового письма.
                    Извлеки из него всю важную информацию для системы RAG. 
                    Нужны вопросы, ключевые параметры, и основные темы обсуждения. Вот текст письма:

                    Текст: \"{text}\"

                    Разбери письмо на следующие компоненты и предоставь в виде шаблона:

                    '1. Все поставленные вопросы.
                    2. Перечень ключевых параметров, упомянутых в тексте.
                    3. Основные темы, которые обсуждаются.'
                    
                    Используй структурированный подход, чтобы я мог легко использовать эти данные для запросов в системе RAG.
                    Без дополнительных комментариев.
                    """

        model_response = chain.invoke(template) 
        return model_response


    # finall function
    def get_response(self, request: str) -> str:
        inquiry = str(request.replace('\n', ' '))
        # abstraction = step_back_prompt(llm, parser, inquiry)
        # print("\n\n---\n\n", abstraction)
        question = self.extract_question(inquiry)
        # print("\n\n---\n\n", question, "\n\n---\n\n")
        response = self.chain.invoke(
            {"question": question},
            return_only_outputs = True
        )["answer"]
        return response

# for testing
# rag = RAGModel()
# while True:
#     query = input()
#     response = rag.get_response(query)
#     print(response)