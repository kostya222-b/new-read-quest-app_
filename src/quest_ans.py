from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

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
        body = await request.json()
        authorization_header = request.headers.get("X-Authorization", "aje7d9vbut2at538rm45")  # Получаем API ключ из заголовка
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
        raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка Yandex GPT: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
