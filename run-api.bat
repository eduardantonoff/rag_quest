if not exist "data\db" mkdir data\db
if not exist "data\db\vector" mkdir data\db\vector
if not exist "data\db\neo4j" mkdir data\db\neo4j
if not exist "data\imported_docs" mkdir data\imported_docs

docker run --rm -v ".\data\imported_docs:/docs" -v ".\data\db\vector:/db" --env-file ./.env  -p 8000:80 rag-quest/api