from fastapi import Request
import httpx
from .news import views as news_views 
from fastapi import  HTTPException
import httpx
from api.village.models import Village
from api.village import schemas
from core.db import db
from fastapi import APIRouter, Request
from core.db import db
from api.village.models import Village

def init_app(app):
    app.include_router(router)
    
    @app.post("/webhook")
    async def telegram_webhook(request: Request):
        data = await request.json()
        print(f"Incoming Update: {data}")

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            
            if "text" in message:
                text       = message["text"]
                user       = message.get("from", {})
                first_name = user.get("first_name", "User")

                if text == "/start":
                    await news_views.handle_start_command(chat_id, first_name)

        return {"ok": True}

    @app.post("/news/submit")
    async def submit_news(request: Request):
        data = await request.json()
        success = await news_views.submit_news(data)
        if success:
            return {"status": "success"}
        else:
            return {"status": "error"}, 500
        
    
    @app.post("/register", response_model=schemas.VillageRead)
    async def register_village(village: schemas.VillageCreate):
        existing_village = db.query(Village).filter(
            Village.unique_id == village.unique_id
        ).first()
        
        if existing_village:
            raise HTTPException(
                status_code=400, 
                detail="A village with this unique_id is already registered."
            )

        new_village = Village(
            unique_id          = village.unique_id,
            name_khmer         = village.name_khmer,
            bot_token          = village.bot_token,
            commune_chat_id    = village.commune_chat_id,
            district_chat_id   = village.district_chat_id,
            province_chat_id   = village.province_chat_id,
            commune_bot_token  = village.commune_bot_token,
            district_bot_token = village.district_bot_token

        )

        try:
            db.add(new_village)
            db.commit()
            db.refresh(new_village)

            base_url = "https://grateful-usable-hedy.ngrok-free.dev" 
            webhook_url = f"{base_url}/webhook/{new_village.unique_id}"
            telegram_api_url = f"https://api.telegram.org/bot{new_village.bot_token}/setWebhook"

            async with httpx.AsyncClient() as client:
                webhook_res = await client.post(telegram_api_url, params={"url": webhook_url})
                result = webhook_res.json()
                
                if not result.get("ok"):
                    print(f"⚠️ Warning: Database saved but Webhook failed: {result.get('description')}")
                else:
                    print(f"🚀 Webhook auto-configured for {new_village.unique_id}")

            return new_village

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
router = APIRouter()
    
@router.post("/webhook/{v_id}")
async def village_webhook(v_id: str, request: Request):
    data = await request.json()
    
    village_data = db.query(Village).filter(Village.unique_id == v_id).first()
    
    if village_data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        first_name = message.get("from", {}).get("first_name", "User")
        await news_views.handle_start_command(chat_id, first_name, village_data)
        
    return {"ok": True}
