from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://iomqt-vo.edu.rosminzdrav.ru",
        "http://localhost",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/api/proxy-yandex-gpt')
async def proxy_yandex_gpt(request: Request):
    try:
        logger.info(f"Headers: {dict(request.headers)}")  # Логируем все заголовки
        body = await request.json()
        authorization_header = request.headers.get("x-authorization", "aje7d9vbut2at538rm45")
        logger.info(f"Authorization header: {authorization_header}")  # Логируем заголовок авторизации

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {authorization_header}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                json=body,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}, {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка Yandex GPT: {e.response.text}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
