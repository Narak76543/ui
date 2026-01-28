from fastapi import Request
from .news import views as news_views # Ensure this import is at the top

def init_app(app):
    
    @app.post("/webhook")
    async def telegram_webhook(request: Request):
        data = await request.json()
        print(f"Incoming Update: {data}")

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            
            if "text" in message:
                text = message["text"]
                user = message.get("from", {})
                first_name = user.get("first_name", "User")

                # --- THIS IS WHERE YOU PUT IT ---
                if text == "/start":
                    await news_views.handle_start_command(chat_id, first_name)
                # --------------------------------

        return {"ok": True}

    @app.post("/news/submit")
    async def submit_news(request: Request):
        data = await request.json()
        success = await news_views.submit_news(data)
        if success:
            return {"status": "success"}
        else:
            return {"status": "error"}, 500
        
        