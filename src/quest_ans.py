import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser

# Пути к файлам
MYANS_PATH = 'src/myans.txt'
INDEX_DIR = 'src/indexdir'

# Схема индекса Whoosh
schema = Schema(
    question=TEXT(analyzer=StemmingAnalyzer()),
    answer=TEXT(analyzer=StemmingAnalyzer())
)

# Инициализация FastAPI
tags_metadata = [
    {
        'name': 'SEARCH ANSWERS',
        'description': 'API для поиска правильных ответов.',
    }
]

origin_endpoint = [
    'https://iomqt-vo.edu.rosminzdrav.ru',
    'https://iomqt-spo.edu.rosminzdrav.ru',
    'https://iomqt-nmd.edu.rosminzdrav.ru'
]

app = FastAPI(
    root_path="/api",
    title='API for SEARCH ANSWERS',
    description='API для поиска правильных ответов',
    version='0.1.0',
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_endpoint,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_last_modified_time(file_path):
    """Возвращает время последнего изменения файла."""
    return os.path.getmtime(file_path)

def rebuild_index_if_needed():
    """
    Пересоздаёт индекс Whoosh, если файл myans.txt изменился.
    """
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR, exist_ok=True)
        needs_rebuild = True
    else:
        index_time = get_last_modified_time(INDEX_DIR)
        file_time = get_last_modified_time(MYANS_PATH)
        needs_rebuild = file_time > index_time

    if needs_rebuild:
        print("myans.txt изменился. Пересоздаём индекс Whoosh...")
        ix = create_in(INDEX_DIR, schema)
        writer = ix.writer()
        with open(MYANS_PATH, 'r', encoding='utf-8') as f:
            current_question = None
            current_answers = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line[0].isdigit() and '.' in line:
                    # Сохраняем предыдущий вопрос и ответы
                    if current_question:
                        writer.add_document(
                            question=current_question,
                            answer='\n'.join(current_answers)
                        )
                    # Начинаем новый вопрос
                    current_question = line.split('. ', 1)[1]
                    current_answers = []
                elif line.endswith('+'):
                    current_answers.append(line[:-1].strip())
        # Сохраняем последний вопрос
        if current_question:
            writer.add_document(
                question=current_question,
                answer='\n'.join(current_answers)
            )
        writer.commit()
        print("Индекс успешно пересоздан!")
    else:
        print("Индекс актуален. Используем существующий.")

def search_whoosh(quest: str):
    """
    Выполняет поиск по актуальному индексу Whoosh.
    Возвращает список правильных ответов.
    """
    rebuild_index_if_needed()
    ix = open_dir(INDEX_DIR)
    with ix.searcher() as searcher:
        query = QueryParser("question", ix.schema).parse(quest)
        results = searcher.search(query, limit=1)
        if results:
            hit = results[0]
            return hit['answer'].split('\n')
        else:
            return []

@app.get('/test')
async def test(quest: str = None):
    if not quest:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')
    true_answers_list = search_whoosh(quest)
    if not true_answers_list:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')
    return true_answers_list
