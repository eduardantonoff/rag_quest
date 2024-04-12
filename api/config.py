from typing import Optional
import os


class Config:
    GPN_API_DATABASE_DIR: Optional[str]
    GPN_API_IMPORTED_DOCS_DIR: Optional[str]

    def __init__(self):
        self._database_dir = None
        self._imported_docs_dir = None
        self.GPN_API_DATABASE_DIR = os.getenv('GPN_API_DATABASE_DIR')
        self.GPN_API_IMPORTED_DOCS_DIR = os.getenv('GPN_API_IMPORTED_DOCS_DIR')
        self.load_config()

    def load_config(self) -> None:
        if not self.GPN_API_DATABASE_DIR or not self.GPN_API_IMPORTED_DOCS_DIR:
            raise ValueError("Missing configuration values")

        self._database_dir = os.path.abspath(self.GPN_API_DATABASE_DIR)
        if not os.path.exists(self._database_dir):
            os.makedirs(self._database_dir)

        self._imported_docs_dir = os.path.abspath(self.GPN_API_IMPORTED_DOCS_DIR)
        if not os.path.exists(self._imported_docs_dir):
            os.makedirs(self._imported_docs_dir)

    def get_imported_file_path(self, path: str) -> str:
        return os.path.join(self._imported_docs_dir, path)

    def dump(self) -> None:
        print(f"GPN_API_DATABASE_DIR: {self.GPN_API_DATABASE_DIR}")
        print(f"GPN_API_IMPORTED_DOCS_DIR: {self.GPN_API_IMPORTED_DOCS_DIR}")
        print(f"database_dir: {self._database_dir}")
        print(f"imported_docs_dir: {self._imported_docs_dir}")

    @property
    def database_dir(self) -> Optional[str]:
        return self._database_dir

    @property
    def imported_docs_dir(self) -> Optional[str]:
        return self._imported_docs_dir
