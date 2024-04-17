from docx2txt import process as process_docx
from pdfplumber import open as open_pdf
import os
import re
from rag import RAGModel
from config import Config


class DataConverter:
    def __init__(self):
        pass

    @staticmethod
    def pdf_to_text(path: str) -> str:
        extracted_text = []
        # Параметры (TODO: придумать, как их лучше передавать)
        crop_coords = [0.05, 0.04, 0.94, 0.95]
        end_of_line_list = ['.', ':', ';']
        min_font_size = 10
        with open_pdf(path) as pdf:
            line_buffer = ''
            for page in pdf.pages:
                # Ограничение области обработки исходной страницы,
                # чтобы не попадали номера страниц и т д
                my_width = page.width
                my_height = page.height
                my_bbox = (crop_coords[0] * float(my_width), crop_coords[1] * float(my_height),
                           crop_coords[2] * float(my_width), crop_coords[3] * float(my_height))
                page_crop = page.crop(bbox=my_bbox)
                text_lines = page_crop.extract_text_lines(x_tolerance=1)
                for item in text_lines:
                    # Игнорирование мелкого шрифта (примечания, таблицы)
                    if float(item['chars'][0]['size']) >= min_font_size:
                        text_line = item['text']
                        if text_line.strip():
                            # Каждая строка в итоговом тексте должна
                            # начинаться с номера (буллита):
                            if re.match(r'^\d+(\.\d+)*\.', text_line.strip()):
                                if line_buffer == '':
                                    line_buffer = text_line
                                else:
                                    extracted_text.append(line_buffer)
                                    line_buffer = text_line
                            elif line_buffer == '':
                                line_buffer = text_line
                            else:
                                line_buffer = line_buffer + ' ' + text_line
                            # Если найден символ конца строки:
                            if text_line.split()[-1][-1] in end_of_line_list:
                                extracted_text.append(line_buffer)
                                line_buffer = ''
        return '\n'.join(extracted_text)

    @staticmethod
    def docx_to_text(path: str) -> str:
        text = process_docx(path)
        return text


class DataProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.rag = RAGModel(config)

    def update_db(self, doc_path: str) -> None:
        extension = os.path.splitext(doc_path)[-1]
        file_name = os.path.basename(doc_path)
        file_id = os.path.splitext(file_name)[0]

        text = ""
        if extension == '.pdf':
            text = DataConverter.pdf_to_text(doc_path)
        elif extension == '.docx':
            text = DataConverter.docx_to_text(doc_path)
        elif extension == '.txt':
            with open(doc_path, 'r') as file:
                text = file.read()

        db_file_path = os.path.join(self.config.database_dir, file_id + ".txt")
        with open(db_file_path, 'w', encoding='utf-8') as file:
            file.write(text)

    def query(self, query_text: str) -> str:
        return self.rag.get_response(query_text)
