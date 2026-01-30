from datetime import datetime
import httpx
import os
from api.news.models import News
from api.village.models import Village
from core.db import db
import asyncio

async def handle_start_command(chat_id: int, first_name: str, village_info=None):
    if village_info:
        token  = village_info.bot_token
        v_name = village_info.name_khmer
        v_id   = village_info.unique_id
    else:
        token  = os.getenv("BOT_TOKEN")
        v_name = "ប្រព័ន្ធ"
        v_id   = "default"

    ui_url = f"https://html-sigma-liart.vercel.app/?chat_id={chat_id}&v_id={v_id}"
    
    welcome_text = (
        
        f"🙏🏻 Hello ! {first_name}!\n\n"
        # f"សូមស្វាគមន៍មកកាន់ប្រព័ន្ធរាយការណ៍សម្រាប់ **{v_name}**. 🇰🇭\n\n"
        f"Welcome to the {v_name} Reporting Bot 🏘️\n\n"
        f"You are now connected to the official reporting gateway for {v_name}\n\n"
        f"This bot helps forward important information to the Commune and District levels."
    )

    payload = {
        "chat_id"   : chat_id,
        "text"      : welcome_text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "🚀 Open Report Form", "web_app": {"url": ui_url}}
            ]]
        }
    }

    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        await client.post(url, json=payload)

async def submit_news(data: dict):

    v_id = data.get("v_id")
    print(f"DEBUG: ទទួលបាន v_id ពី Frontend: {v_id}")
    
    title   = data.get("title", "គ្មានចំណងជើង")
    sender  = data.get("sender_name", "មិនស្គាល់អត្តសញ្ញាណ")
    content = data.get("content", "គ្មានខ្លឹមសារ")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    village_info = db.query(Village).filter(Village.unique_id == v_id).first()

    if not village_info:
        print(f"❌ រកមិនឃើញភូមិដែលមាន ID: {v_id} ក្នុង Database ឡើយ")
        return False

    try:
        new_entry = News(
            village_name = village_info.name_khmer, 
            commune_name = f"រដ្ឋបាលឃុំ (តាមរយៈ {v_id})", 
            title        = title,
            content      = content,
            created_at   = datetime.now()
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        print(f"✅ បានរក្សាទុករួចរាល់ក្នុង DB: ID {new_entry.id}")
    except Exception as e:
        db.rollback() 
        print(f"❌ Database Error: {e}")
    
    message_text = (
        f"📢 មានរបាយការណ៍ថ្មីពី៖ {village_info.name_khmer}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 អ្នករាយការណ៍: {sender}\n"
        f"🏘️ ភូមិ: {village_info.name_khmer}\n"
        f"🕒 កាលបរិច្ឆេទ: {current_time}\n"
        f"📌 ចំណងជើង: {title}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 ខ្លឹមសារ:\n{content}"
    )

    async with httpx.AsyncClient() as client:
        try:
            if village_info.commune_chat_id:
                await client.post(
                    f"https://api.telegram.org/bot{village_info.bot_token}/sendMessage",
                    json={"chat_id": village_info.commune_chat_id, "text": message_text}
                )
            if village_info.district_chat_id and village_info.commune_bot_token:
                res_d = await client.post(
                    f"https://api.telegram.org/bot{village_info.commune_bot_token}/sendMessage",
                    json={"chat_id": village_info.district_chat_id, "text": f"🔄 Summary for District:\n{message_text}"}
                )
                print(f"District Forward: {res_d.json()}")

            if village_info.province_chat_id and village_info.district_bot_token:
                res_p = await client.post(
                    f"https://api.telegram.org/bot{village_info.district_bot_token}/sendMessage",
                    json={"chat_id": village_info.province_chat_id, "text": f"🔄 Final Report for Province:\n{message_text}"}
                )
                print(f"Province Forward: {res_p.json()}")

        except Exception as e:
            print(f"Error: {e}")
