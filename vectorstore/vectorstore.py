import os

from langchain_core.embeddings import Embeddings
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores.faiss import FAISS


class Index():
    '''
    Vector index.

    Embedding:
        DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
    '''

    def __init__(self, data_path: str, index_name: str, embeddings: Embeddings) -> None:
        '''
        Reading the index if exists.
        '''

        self.data_path = data_path
        self.index_name = index_name
        self.embeddings = embeddings

        try:
            self.index = FAISS.load_local(data_path, index_name, embeddings, allow_dangerous_deserialization=True)
        except:
            self.index = None

    def loadDocuments(self, documents):
        '''
        Loading documents. Initialize the index if needed.
        '''

        if not self.index:
            self.index = FAISS.from_documents(documents, self.embeddings)
        else:
            self.index.add_documents(documents)

        self.save()

        return self

    def retriever(self):
        if not self.index:
            raise Exception("The index is not initialized. Load documents first.")

        return self.index.as_retriever()

    def save(self):
        '''
        Save the index.
        '''

        if not self.index:
            raise Exception("The index is not initialized. Load documents first.")

        self.index.save_local(self.data_path, self.index_name)

        return self


class Store():
    '''
    A set of fabric tools to handle indexes.
    '''

    # TODO: to config file
    data_path = './data'

    @classmethod
    def indexes(cls):
        '''
        Return list of indexes.
        '''

        # TODO: list of indexes
        return []

    @classmethod
    def exist(cls, name: str):
        # TODO: check existance
        return True

    @classmethod
    def getIndex(cls, index_name: str = 'index'):
        '''
        Get index by name. Try to load it.
        '''

        # check if data folder doesnt exist
        if not os.path.exists(cls.data_path):
            os.mkdir(cls.data_path)

        # TODO: make it a choosable
        embeddings = SentenceTransformerEmbeddings()

        return Index(cls.data_path, index_name, embeddings)

    @classmethod
    def delete(cls, name: str = 'index'):

        # TODO: delete
        return True
