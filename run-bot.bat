if not exist "data\imported_docs" mkdir data\imported_docs

docker run --rm -v ".\data\imported_docs:/docs" --env-file ./.env rag-quest/chatbot