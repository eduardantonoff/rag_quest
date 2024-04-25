import os
import re
from langchain_core import documents


class CustomTextSplitter:
    def __init__(self, target_chunk_size=1000):

        self.target_chunk_size = target_chunk_size
        self.source = ''
        self.file_hash = ''
        self.chunks = []
        self.current_chunk = ''
        self.dcts = []
        self.bullet_name = ''
        self.prev_bullet_name = ''
        self.mode_list = ['bullet', 'line', 'space']
        self.sep_dict = {'line': '\n', 'space': ' '}
        self.link_dict = {'bullet': '\n', 'line': '\n', 'space': ' '}

    @staticmethod
    def is_bullet(line: str):
        # Проверка, начинается ли строка с буллита
        return re.match(r'(\d+(\.\d+)*\.\d+)\.?', line.strip())

    def make_chunks(self, input_text: str, mode: str):
        link = self.link_dict[mode]
        if len(input_text) == 0:
            return
        if len(self.current_chunk) > 0:
            # Если текущий чанк не пуст, проверяем, поместится ли туда текущий фрагмент
            new_chunk = self.current_chunk + link + input_text
            if len(new_chunk) <= self.target_chunk_size and mode != 'bullet':
                self.current_chunk = new_chunk
            else:
                # Сначала сохраняем текущий чанк, потом
                # в текущий чанк записываем новый фрагмент
                self.chunks.append(self.current_chunk)
                dct = documents.base.Document(self.current_chunk)
                dct.metadata = {'source': self.source}
                # Записываем имя буллита чанка в метаданные
                if mode == 'bullet':
                    dct.metadata['bullet'] = self.prev_bullet_name
                else:
                    dct.metadata['bullet'] = self.bullet_name
                self.dcts.append(dct)
                self.current_chunk = ''
                if len(input_text) <= self.target_chunk_size:
                    self.current_chunk = input_text
                else:
                    # Текст не помещается в чанк целиком. Тогда определяем параметры нового
                    # разбиения и вызываем рекурсивно этот же метод.
                    next_mode, separator = self.prepare_for_new_split(mode)
                    if next_mode is None:
                        return
                    else:
                        for item in input_text.split(separator):
                            self.make_chunks(item, next_mode)
                        # После завершения разбиения сохраняем текущий чанк, если он не пуст.
                        if self.current_chunk != '':
                            self.chunks.append(self.current_chunk)
                            dct = documents.base.Document(self.current_chunk)
                            # В текущей реализации в метаданные пишется имя последнего буллита чанка
                            dct.metadata = {'source': self.source, 'bullet': self.bullet_name}
                            self.dcts.append(dct)
                            self.current_chunk = ''
        elif len(input_text) <= self.target_chunk_size:
            self.current_chunk = input_text
        else:
            # Текст не помещается в чанк целиком. Тогда определяем параметры нового
            # разбиения и вызываем рекурсивно этот же метод.
            next_mode, separator = self.prepare_for_new_split(mode)
            if next_mode is None:
                return
            else:
                for item in input_text.split(separator):
                    self.make_chunks(item, next_mode)
                # После завершения разбиения сохраняем текущий чанк, если он не пуст.
                if self.current_chunk != '':
                    self.chunks.append(self.current_chunk)
                    dct = documents.base.Document(self.current_chunk)
                    # Записываем имя буллита чанка в метаданные
                    dct.metadata = {'source': self.source, 'bullet': self.bullet_name}
                    self.dcts.append(dct)
                    self.current_chunk = ''

    def prepare_for_new_split(self, current_mode: str):
        # Определяем параметры разбиения
        next_mode_index = self.mode_list.index(current_mode) + 1
        if next_mode_index < len(self.mode_list):
            next_mode = self.mode_list[next_mode_index]
            next_separator = self.sep_dict[next_mode]
            return next_mode, next_separator
        else:
            return None, None

    def split_text(self, text: str, source: str, file_hash: str):
        bullet_chunks = []
        current_bullet_chunk = ''
        self.file_hash = file_hash
        self.source = os.path.splitext(os.path.basename(source))[0]
        # Разбиваем исходный текст на куски, каждый из которых (кроме первого)
        # начинается с буллита
        lines = text.split("\n")
        for line in lines:
            if len(line) > 0:
                if self.is_bullet(line):
                    if len(current_bullet_chunk) > 0:
                        bullet_chunks.append(current_bullet_chunk)
                    current_bullet_chunk = line
                elif len(current_bullet_chunk) > 0:
                    current_bullet_chunk = current_bullet_chunk + '\n' + line
                else:
                    current_bullet_chunk = line
        bullet_chunks.append(current_bullet_chunk)
        # Для каждого буллита сохраняем его имя (=номер) и вызываем метод разбивки на чанки
        for bc in bullet_chunks:
            if len(bc) > 0:
                self.prev_bullet_name = self.bullet_name
                if self.is_bullet(bc):
                    self.bullet_name = self.is_bullet(bc).group()
                else:
                    self.bullet_name = bc.split()[0]
                self.make_chunks(bc, 'bullet')

        return self.dcts
