from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://iomqt-vo.edu.rosminzdrav.ru",
        "http://localhost",
        "http://localhost:3000",
        "chrome-extension://*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обработчик OPTIONS-запросов
@app.options("/api/proxy-mistral")
async def options_handler(request: Request):
    return {"status": "ok"}

# Прокси-эндпоинт для Mistral AI
@app.post('/api/proxy-mistral')
async def proxy_mistral(request: Request):
    try:
        body = await request.json()
        api_key = "vIbfcVlLsLylHUHN19BiZUyc6amzLSVE"  # Ваш API-ключ Mistral AI

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                json=body,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}, {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка Mistral AI: {e.response.text}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
