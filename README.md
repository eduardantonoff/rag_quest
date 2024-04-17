# Структура проекта

```

├───api (сервис REST API)
│   └─── // исходный код и конфигурация сервиса API
│
├───chatbot (сервис Telegram bot)
│   └─── // исходный код и конфигурация сервиса chatbot
│
├───data (рабочие данные проекта)
│   ├──── db //сюда мамятся данные vectorstorage и neo4j
│   ├──── imported_docs //сюда API сохраняет загруженные документы в исходном формате
│   └──── training_docs //отсюда скрипт upload_docs.bat загружает в API документы поддерживаемых типов
│
├───explore (ноутбуки jupyter и другие файлы для экспериметов и тестов RAG и neo4j)
│
├───utils (вспомогательные скрипты)
│
скрипты и конфиги общие для всего проекта

```

# Как работать с проектом в режиме разработки

- Скачать проект командой git pull. 
- Активировать глобальную конфигурацию python в версию 3.8 (одно из требований к результатам хакатона).
- Перейти в целевой сервис и сконфигурировать виртуальное окружение командой python -m venv .venv (если еще не создано)
- Активировать окружение в этом фолдере командой ./.venv/bin/activate (для Linux, MacOs; возможно придется назначить атрибут выполняемого файла командой chmod +x ./.venv/bin/activate) или .\.venv\scripts\activate для Windows
- Если окружение активировано (а это видно по промпту в консоли) то установить пакеты командой python -m pip install -r requirements.txt

Код структурирован так чтобы не было зависимостей по коду между сервисами и вообще другими фолдерами проекта. Параметры настройки вынесены в .env файлы (которые надо создать перед запуском сервисов проекта - см файлы template.env в качестве шаблонов).
Корневой .env задает параметры для сервисов при выполнении в Docker контейнерах.
Файлы внутри проектов ./api/.env, ./chatbot/.env необязательны но их удобно использовать в среде разработки. Для удобства отладки сервисов можно сконфигурировать загрузку переменных окружения из этих файлов (<project>/.env) перед запуском проекта - в этом случае приоритет будут иметь переменные из этих файлов.

Если в результате разработки поменялся перечень используемых пакетов то изменения следует зафиксировать выполнив команду
pip freeze >requirements.txt в целевом фолдере сервиса. При этом виртуальное окружение должно быть активировано.

Для тестирования отдельных сервисов их контейнеры можно собирать и запускать по отдельности - соотв скриптами *.bat из корня проекта. Пересборку контейнеров надо запускать в том случае если изменился код и/или список зависимостей проекта

Следует поддерживать чистоту папок сервисов  сохраняя там только рабочий код. Файлы данных должны помещаться в фолдеры, вложенные в ./data. Скрипты (или ноутбуки) для экспериментов должны сохраняться в ./explore

Документацию следует помещать в ./docs

# Инициализация базы данных документов 

Запустив сервис API надо поместить целевые документы поддерживаемых форматов (pdf, docx, txt) в папку ./data/training_docs и выполнить скрипт upload_docs.bat из корня проета. Проанализировать вывод скрипта. Если все прошло удачно то в папке ./data/imported_docs должны появиться исходные копии документы переименованные по схеме <original-doc-content-md5-hash>.<original-ext>
а в папке ./data/db/vector то же количество текстовых документов именованных по <original-doc-content-md5-hash>.txt

# API

Tестовая консоль (OpenAPI/Swagger) доступна по URI - /api/explore - в ней можно протестировать основные эндпойнты
По умолчанию полный URL - http://localhost:8000/api/explore

Эндпойнт обработки запросов /api/query работает с текстом (не json) для упрощения визуального анализа возвращаемого результата.
В финальной версии формат будет более стурктурированным для интеграции с ботом и утилитами тестирования.

# Конфигурация Telegram бота 

- Найдите бота `@BotFather` в Telegram и начните диалог. 
- Создайте нового бота, следуя инструкциям  `@BotFather` . 
- Получите уникальный API токен для вашего бота. 
- Установите значение `GPN_CHATBOT_TOKEN=<real telegram api token here>` в файле `.env` в корне проекта (по общей структуре файла см прототип template.env), указав полученный API токен. 

# Интеграция (сделать)
- добавить разрезку и загрузку текстовых документов в векторное хранилище

# Работа с документами 
При загрузке докуммента API сохраняет загруженные документы в папку ./data/imported_docs на хосте (доступны и чатботу тоже на случай доступа к документу по ссылке).  В качестве идентификатора документа выступает md5 хэш содержимого докумнта. Извлеченный из документа текст сохраняется в векторное хранилище (путь ./data/db/vector на хосте) для последующей индексации.

Основной формат обрабатываемых документов - PDF, так как в нём корректно отображается нумерация буллитов (при сохранении в .docx она слетает)

Цель преобразования PDF - выделить текст документа, очищенный от нумерации страниц, таблиц и сносок.
Также в тексте убраны ненужные переносы строк, что облегчает дальнейшее его разбиение и использование.

