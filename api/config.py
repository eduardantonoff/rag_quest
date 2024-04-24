from typing import Optional
import os
from dotenv import load_dotenv


class Config:
    GPN_API_DATABASE_DIR: Optional[str]
    GPN_API_IMPORTED_DOCS_DIR: Optional[str]
    GPN_API_PROMPTS_DIR: Optional[str]

    NEO4J_URI: Optional[str]
    NEO4J_USERNAME: Optional[str]
    NEO4J_PASSWORD: Optional[str]
    NEO4J_DATABASE: Optional[str]

    LLM_SCOPE: Optional[str]
    LLM_AUTH: Optional[str]

    def __init__(self):
        load_dotenv(override=False, encoding='utf-8')

        self._database_dir = None
        self._imported_docs_dir = None
        self._prompts_dir = None

        self.GPN_API_DATABASE_DIR = os.getenv('GPN_API_DATABASE_DIR')
        self.GPN_API_IMPORTED_DOCS_DIR = os.getenv('GPN_API_IMPORTED_DOCS_DIR')
        self.GPN_API_PROMPTS_DIR = os.getenv('GPN_API_PROMPTS_DIR')

        self.NEO4J_URI = os.getenv('NEO4J_URI')
        self.NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
        self.NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
        self.NEO4J_DATABASE = os.getenv('NEO4J_DATABASE')

        self.LLM_SCOPE = os.getenv('SCOPE')
        self.LLM_AUTH = os.getenv('AUTH_DATA')

        self.load_config()

    def load_config(self) -> None:
        if (not self.GPN_API_DATABASE_DIR or
                not self.GPN_API_IMPORTED_DOCS_DIR or
                not self.GPN_API_PROMPTS_DIR or
                not self.NEO4J_URI or not self.LLM_SCOPE or
                not self.LLM_AUTH):
            raise ValueError("Missing mandatory configuration values")

        self._database_dir = os.path.abspath(self.GPN_API_DATABASE_DIR)
        if not os.path.exists(self._database_dir):
            os.makedirs(self._database_dir)

        self._imported_docs_dir = os.path.abspath(self.GPN_API_IMPORTED_DOCS_DIR)
        if not os.path.exists(self._imported_docs_dir):
            os.makedirs(self._imported_docs_dir)

        self._prompts_dir = os.path.abspath(self.GPN_API_PROMPTS_DIR)
        if not os.path.exists(self._prompts_dir):
            os.makedirs(self._prompts_dir)

    def get_imported_file_path(self, path: str) -> str:
        return os.path.join(self._imported_docs_dir, path)

    def dump(self) -> None:
        print(f"GPN_API_DATABASE_DIR: {self.GPN_API_DATABASE_DIR}")
        print(f"GPN_API_IMPORTED_DOCS_DIR: {self.GPN_API_IMPORTED_DOCS_DIR}")
        print(f"GPN_API_PROMPTS_DIR: {self.GPN_API_PROMPTS_DIR}")
        print(f"database_dir: {self._database_dir}")
        print(f"imported_docs_dir: {self._imported_docs_dir}")
        print(f"NEO4J_URI: {self.NEO4J_URI}")

    @property
    def database_dir(self) -> Optional[str]:
        return self._database_dir

    @property
    def imported_docs_dir(self) -> Optional[str]:
        return self._imported_docs_dir

    @property
    def prompts_dir(self) -> Optional[str]:
        return self._prompts_dir


#%%
