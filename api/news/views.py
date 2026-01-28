from datetime import datetime
from fastapi import Depends
import httpx
import os
from sqlalchemy.orm import Session
from api.news.models import News
from core.db import db
import asyncio


async def handle_start_command(chat_id: int, first_name: str):
    bot_token = os.getenv("BOT_TOKEN")
    # Debug: Print the token to your terminal to make sure it's loaded
    print(f"Using Bot Token: {bot_token[:10]}...") 

    ui_url = "https://html-sigma-liart.vercel.app/"
    
    welcome_text = (
        f"🙏🏻 **ជម្រាបសួរ ! {first_name}!**\n\n"
        f"សូមស្វាគមន៍មកកាន់ **ប្រព័ន្ធរាយការពត៌មានតាមភូមិ**. 🇰🇭\n\n"
        f"ប្រព័ន្ធនេះនឹងជួយរាយការណ៍ពត៌មាន ទាំងអស់យ៉ាងរហ័សនៅក្នុងតំបន់របស់យើង​​ "
        f"ពត៌មានទាំងអស់នឹងបញ្ជូនពី **​ភូមី → ឃុំ → ស្រុក → ខេត្ត**.\n\n"
        f"សូមចុច ប៊ូតុងខាងក្រោមដើម្បីរាយការណ៍ពត៌មាន របស់បងប្អូន ។ 🙏🏻."
    )

    payload = {
        "chat_id": chat_id,
        "text": welcome_text,
        "parse_mode": "Markdown", 
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "🚀 Open Reporting Form", "web_app": {"url": ui_url}}
            ]]
        }
    }

    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            response = await client.post(url, json=payload)
            print(f"Telegram Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending to Telegram: {e}")


async def submit_news(data: dict  ):
    bot_token = os.getenv("BOT_TOKEN")
    commune_chat_id = os.getenv("COMMUNE_CHAT_ID")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    village = data.get("village_name", "")
    commune = data.get("commune_name", "")
    title = data.get("title", "")
    content = data.get("content", "")

    try:
        new_entry = News(
            village_name=village,
            commune_name=commune,
            title=title,
            content=content,
            created_at=datetime.now()
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        print(f"✅ Recorded in DB: ID {new_entry.id}")
    except Exception as e:
        db.rollback() 
        print(f"❌ Database Error: {e}")
    
    message_text = (
        f"📢 **មានដំណឹងក្តៅៗ មេ🔥**\n\n"
        f"🕒 **កើតឡើងពេល:** {current_time}\n"
        f"🏘️ **កើតឡើងនៅភូមិ:** {village}\n"
        f"🏛️ **ក្នុងឃុំ:** {commune}\n"
        f"📌 **ចំណងជើង:** {title}\n\n"
        f"📝 **មាតិការ:**\n{content}"
    )
    
    payload = {
        "chat_id": commune_chat_id,
        "text": message_text,
        "parse_mode": "Markdown" 
    }


    v_2_c = 5 
    c_2_d = 10
    d_2_p = 30
    async with httpx.AsyncClient() as client:
            # Send to Commune Group
            await asyncio.sleep(v_2_c)
            await client.post(
                f"https://api.telegram.org/bot{os.getenv('COMMUNE_BOT_TOKEN')}/sendMessage",
                json={"chat_id": os.getenv("COMMUNE_CHAT_ID"), "text": message_text, "parse_mode": "Markdown"}
            )
            
            await asyncio.sleep(c_2_d)
            await client.post(
                f"https://api.telegram.org/bot{os.getenv('DISTRICT_BOT_TOKEN')}/sendMessage",
                json={"chat_id": os.getenv("DISTRICT_CHAT_ID"), "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ស្រុក**\n\n{message_text}", "parse_mode": "Markdown"}
            )
            await asyncio.sleep(d_2_p)
            await client.post(
                f"https://api.telegram.org/bot{os.getenv('PROVINCE_BOT_TOKEN')}/sendMessage",
                json={"chat_id": os.getenv("PROVINCE_CHAT_ID"), "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ខេត្ត**\n\n{message_text}", "parse_mode": "Markdown"}
            )

            return True