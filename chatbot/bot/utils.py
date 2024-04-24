import os

TOKEN = os.getenv('GPN_CHATBOT_TOKEN')
URL = os.getenv('GPN_API_URL')

WELCOME_MESSAGE = """Здравствуйте! 
Я виртуальный ассистент. 
Помогу ответить на ваши вопросы."""

FEEDBACK_MESSAGE = "Пожалуйста, оцените качество ответа виртуального ассистента!"