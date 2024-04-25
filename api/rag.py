import os
import re
import glob
import pickle
import numpy as np
import time
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from typing import List
from sklearn.metrics.pairwise import cosine_similarity

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

from config import Config


class RAGModel:

    @staticmethod
    def init_prompts(prompt_dir: str):
        with open(os.path.join(prompt_dir, "query_template_0.txt"), 'r', encoding='utf-8') as f:
            qt0 = f.read()

        with open(os.path.join(prompt_dir, "query_template_1.txt"), 'r', encoding='utf-8') as f:
            qt1 = f.read()

        with open(os.path.join(prompt_dir, "query_template_2.txt"), 'r', encoding='utf-8') as f:
            qt2 = f.read()

        with open(os.path.join(prompt_dir, "query_template_3.txt"), 'r', encoding='utf-8') as f:
            qt3 = f.read()

        return qt0, qt1, qt2, qt3

    def load_index(self):
        path = self.config.collections_dir
        collections = glob.glob(path + '**/*.pkl', recursive=True)

        for file in collections:
            with open(file, 'rb') as f:
                chunks = pickle.load(f)
            self.update_chunks(chunks)

        return self.vector_store

    def wait_for_neo4j(self, uri, user, password, timeout=60):
        # Create driver
        driver = GraphDatabase.driver(uri, auth=(user, password))

        start_time = time.time()
        while True:
            try:
                # Try to create a session
                with driver.session() as session:
                    # Try to run a simple query
                    session.run("MATCH (n) RETURN n LIMIT 1")
                # If we got to this line, then all commands were successful
                print("Neo4j is available, proceeding...")
                break

            except ServiceUnavailable as e:
                # Catch exception when neo4j is not available
                if time.time() - start_time > timeout:
                    # If we've waited too long, raise the exception to the caller
                    print("Couldn't establish connection in the specified timeout.")
                    raise e
                else:
                    # If we haven't passed the timeout, wait for a while and retry
                    print("Connection unsuccessful, retrying...")
                    time.sleep(1)

    def __init__(self, cfg: Config) -> None:
        self.config = cfg

        self.embeddings = GigaChatEmbeddings(credentials=self.config.LLM_AUTH, verify_ssl_certs=False)

        self.wait_for_neo4j(self.config.NEO4J_URI, self.config.NEO4J_USERNAME, self.config.NEO4J_PASSWORD)

        self.graph = Neo4jGraph(
            url=self.config.NEO4J_URI,
            username=self.config.NEO4J_USERNAME,
            password=self.config.NEO4J_PASSWORD,
            database=self.config.NEO4J_DATABASE)

        try:
            self.vector_store = Neo4jVector.from_existing_index(self.embeddings,
                                                                url=self.config.NEO4J_URI,
                                                                username=self.config.NEO4J_USERNAME,
                                                                password=self.config.NEO4J_PASSWORD,
                                                                node_label="Bullet",
                                                                index_name="bullet",
                                                                keyword_index_name="word",
                                                                search_type='hybrid',
                                                                )
        except:
            self.vector_store = self.load_index()

        self.llm = GigaChat(model="GigaChat-Pro",  # "GigaChat-Pro" / "GigaChat-Plus" (32k)
                            temperature=0.3,
                            top_p=0.2,
                            n=1,
                            repetition_penalty=1,
                            credentials=self.config.LLM_AUTH,
                            verify_ssl_certs=False)

        self.parser = StrOutputParser()
        self.qt0, self.qt1, self.qt2, self.qt3 = RAGModel.init_prompts(self.config.prompts_dir)
        self.prompt = ChatPromptTemplate.from_template(self.qt0)
        self.llm.get_num_tokens(self.qt0)
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={
                "k": 10, 'score_threshold': 0.95, 'lambda_mult': 0.25
            })

        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm,  # pro / plus
            chain_type="stuff",
            # "stuff" / "map_rerank" / "refine"
            retriever=self.retriever,
            return_source_documents=True,
            reduce_k_below_max_tokens=True,
            max_tokens_limit=8000,  # up to 32k with plus model
            chain_type_kwargs={"verbose": False,
                               "prompt": self.prompt,
                               "document_variable_name": "context"})

    def extract_question(self, text: str, template_id: int = 1) -> str:
        chain = self.llm | self.parser

        if template_id == 1:
            template = self.qt1.format(text=text)
        elif template_id == 2:
            template = self.qt2.format(text=text)
        elif template_id == 3:
            template = self.qt3.format(text=text)
        else:
            raise ValueError("Invalid template_id value. Expected a number in a range 1 .. 3")

        question = chain.invoke(template).replace('/', ' ')
        return question

    def handle_query(self, query: str, template_id: int = 1) -> any:
        inquiry = str(query.replace('\n', ' '))
        question = self.extract_question(inquiry, template_id)
        resp = self.chain.invoke({"question": question}, return_only_outputs=False)
        if 'question' not in resp:
            resp['question'] = question
        return resp

    def find_relevant_bullets(self, inquiry: str) -> List[str]:
        match = re.search(r'(\d+\.\d+)(?:\.\d+)?', inquiry)

        if match:
            number = match.group(1)

            cypher = f"""
                        MATCH (n:Document)
                        WHERE n.bullet STARTS WITH '{number}' AND n.bullet IS NOT NULL
                        RETURN n.text
                        """
            mentioned_bullets = self.graph.query(cypher)

            if mentioned_bullets:
                texts = [bullet['n.text'] for bullet in mentioned_bullets]

                all_embeddings = [self.embeddings.embed_query(text) for text in texts] + [
                    self.embeddings.embed_query(inquiry)]
                inquiry_embedding = all_embeddings[-1]
                bullet_embeddings = all_embeddings[:-1]

                similarities = cosine_similarity([inquiry_embedding], bullet_embeddings)[0]
                top_indices = np.argsort(similarities)[::-1][:3]
                top_texts = [texts[i] for i in top_indices]

                return top_texts
            else:
                return ["Отсутствуют"]
        else:
            return ["Отсутствуют"]

    @staticmethod
    def get_bullets_or_source(resp: any) -> []:
        bullets = []
        for doc in resp['source_documents']:
            bullet = doc.metadata.get('bullet')
            if bullet is None:
                bullet = doc.metadata.get('source')
            bullets.append(bullet)
        return bullets

    def update_chunks(self, doc_chunks: any) -> None:
        if self.is_remote_db:  # temporary lock for preconfigured db update
            return

        self.vector_store = Neo4jVector.from_documents(
            doc_chunks, self.embeddings,
            url=self.config.NEO4J_URI,
            username=self.config.NEO4J_USERNAME,
            password=self.config.NEO4J_PASSWORD,
            node_label="Bullet",
            index_name="bullet",
            keyword_index_name="word",
            search_type='hybrid',
        )

        self.retriever = self.vector_store.as_retriever(
            search_kwargs={
                "k": 10, 'score_threshold': 0.95, 'lambda_mult': 0.25
            })

    @property
    def is_remote_db(self) -> bool:
        return self.config.NEO4J_URI.lower().endswith("neo4j.io")


# for testing
if __name__ == "__main__":
    config = Config()
    config.dump()

    rag = RAGModel(config)
    while True:
        test_query = input()
        response = rag.handle_query(test_query)
        print(response)
