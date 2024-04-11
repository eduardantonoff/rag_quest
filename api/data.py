import docx2txt
import pdftotext
import os


class DataConverter:
    def __init__(self):
        pass

    @staticmethod
    def pdf_to_text(path: str) -> str:
        with open(path, "rb") as pdf_file:
            pages = pdftotext.PDF(pdf_file)
            extracted_text = "\n\n".join(pages)
        return extracted_text

    @staticmethod
    def docx_to_text(path: str) -> str:
        text = docx2txt.process(path)
        return text


class DataProcessor:
    def __init__(self, db_path: str):
        self.db_path = db_path

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

        db_file_path = os.path.join(self.db_path, file_id + ".txt")
        with open(db_file_path, 'w', encoding='utf-8') as file:
            file.write(text)

    def query(self, query_text: str) -> str:
        # TODO: integrate query processing logic here
        detected_questions_section_content = "..."
        suitable_chunks_section_content = "..."
        final_answer_section_content = "..."

        detected_questions_section_caption = ">>>>>>>>>>>>>>>>>>>>>>>>> Извлеченные вопросы >>>>>>>>>>>>>>>>>>>>>>>>>"
        suitable_chunks_section_caption = "<<<<<<<<<<<<<<<<<<<<<<<< Подходящие чанки текста из базы знаний <<<<<<<<<<<<<<<<<<<<<<<<"
        final_answer_section_caption = "<<<<<<<<<<<<<<<<<<<<<<<< Финальный ответ <<<<<<<<<<<<<<<<<<<<<<<<"

        return f'''
        {detected_questions_section_caption}
        
        {detected_questions_section_content}
        
        
        
        {suitable_chunks_section_caption}
        
        {suitable_chunks_section_content}
        
        
        
        {final_answer_section_caption}
        
        {final_answer_section_content}
        '''
