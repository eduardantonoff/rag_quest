import logging
import os
import tempfile
from hashlib import md5
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Body
from fastapi.responses import JSONResponse, PlainTextResponse

from config import Config
from data import DataConverter, DataProcessor

logger = logging.getLogger("uvicorn")
log_config = uvicorn.config.LOGGING_CONFIG
log_config['formatters']['default']['fmt'] = '%(asctime)s [%(levelname)s] - %(message)s'
log_config['level'] = 'debug'

load_dotenv(override=False, encoding='utf-8')

config = Config()
config.dump()
dp = DataProcessor(db_path=config.database_dir)

router = APIRouter()

supported_file_types = ['.pdf', '.docx', '.txt']


@router.post("/docs/upload/")
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    extension = os.path.splitext(file.filename)[-1]
    if extension not in supported_file_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()
    checksum = md5(content).hexdigest()

    unique_filename = checksum + extension

    details = f"uploaded file '{file.filename}' is stored as {unique_filename}"

    imported_file_path: str = config.get_imported_file_path(unique_filename)
    with open(imported_file_path, "wb") as buffer:
        buffer.write(content)

    dp.update_db(imported_file_path)

    return JSONResponse(
        status_code=200,
        content={"message": "File uploaded successfully", "checksum": checksum, "details": details}
    )


@router.post("/query")
async def new_endpoint(body: str = Body(..., media_type="text/plain")) -> PlainTextResponse:
    return PlainTextResponse(dp.query(body))


@router.get("/")
async def read_root():
    return {"statue": "GPN RAG Quest API is up and running"}


@router.post("/docs/to-text/")
async def extract_text(file: UploadFile = File(...)) -> PlainTextResponse:
    extension = os.path.splitext(file.filename)[-1]
    if extension not in supported_file_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    text = ""

    try:
        temp_file.write(content)
        temp_file.close()
        if extension == '.pdf':
            text = DataConverter.pdf_to_text(temp_file.name)
        elif extension == '.docx':
            text = DataConverter.docx_to_text(temp_file.name)
        elif extension == '.txt':
            text = content

    except Exception as e:
        text = f"{str(e)}"
        print(f"An error occurred during text extraction: {e}")

    finally:
        os.unlink(temp_file.name)

    return PlainTextResponse(text, media_type="text/plain")


app = FastAPI(docs_url="/api/explore")
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8000  # will be overloaded by command line param while running in Docker

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config['loggers']['uvicorn']['level'] = 'DEBUG'
    log_config['loggers']['uvicorn.error']['level'] = 'DEBUG'
    log_config['loggers']['uvicorn.access']['level'] = 'DEBUG'

    uvicorn.run(app, host=HOST, port=PORT, log_level="debug", log_config=log_config)

    print(f"Server is ready and listening at http://{HOST}:{PORT}")

