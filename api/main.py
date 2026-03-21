from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# Разрешаем запросы от твоей игры
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ТВОИ ДАННЫЕ
FOLDER_ID = "b1gfkid3b0smep8do3od"
API_KEY = "AQVNyh5_0yhx8aEL2L_JU6VLUwMC0M46wDNdteeY"

class RequestModel(BaseModel):
    message: str
    history: list = []
    system: str = "Ты — Буклик, добрый помощник для девочки 7 лет. Пиши 3-4 предложения, красиво, с волшебством."

@app.post("/")
async def chat(request: RequestModel):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers={
                    "Authorization": f"Api-Key {API_KEY}",
                    "Content-Type": "application/json",
                    "x-folder-id": FOLDER_ID
                },
                json={
                    "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.8,
                        "maxTokens": 300
                    },
                    "messages": [
                        {"role": "system", "text": request.system},
                        *request.history,
                        {"role": "user", "text": request.message}
                    ]
                }
            )
            data = response.json()
            reply = data.get("result", {}).get("message", {}).get("text", "...")
            
            new_history = [
                *request.history,
                {"role": "user", "text": request.message},
                {"role": "assistant", "text": reply}
            ]
            
            return {"reply": reply, "history": new_history}
    except Exception as e:
        return {"reply": f"Ошибка: {str(e)}", "history": request.history}
