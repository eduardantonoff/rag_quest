from fastapi.testclient import TestClient
from service import app

client = TestClient(app)


def test_upload_pdf_file():
    file_path = 'sample.pdf'  
    files = {'files': ('sample.pdf', open(file_path, 'rb'), '.pdf')}
    response = client.post("/api/docs/upload/", files=files)
    assert response.status_code == 200
    assert response.json() == {"message": "Files uploaded successfully"}


def test_upload_word_file():
    file_path = 'sample.docx' 
    files = {'files': (
    'sample.docx', open(file_path, 'rb'), '.docx')}
    response = client.post("/api/docs/upload/", files=files)
    assert response.status_code == 200
    assert response.json() == {"message": "Files uploaded successfully"}


def test_upload_unsupported_file_type():
    file_path = 'sample.png'  # Ensure you have a sample text file at this location
    files = {'files': ('sample.png', open(file_path, 'rb'), '.png')}
    response = client.post("/api/docs/upload/", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json().get("detail")
