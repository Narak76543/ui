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
        f"🙏🏻 **ជម្រាបសួរ ! {first_name}!**\n\n"
        f"សូមស្វាគមន៍មកកាន់ប្រព័ន្ធរាយការណ៍សម្រាប់ **{v_name}**. 🇰🇭\n\n"
        f"ព័ត៌មានទាំងអស់នឹងបញ្ជូនពី **​ភូមី → ឃុំ → ស្រុក → ខេត្ត**.\n\n"
        f"សូមចុច ប៊ូតុងខាងក្រោមដើម្បីរាយការណ៍ព័ត៌មាន។ សូមអរគុណ​ 🙏🏻."
    )

    payload = {
        "chat_id"   : chat_id,
        "text"      : welcome_text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "🚀 បើកទម្រង់រាយការណ៍", "web_app": {"url": ui_url}}
            ]]
        }
    }

    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        await client.post(url, json=payload)


# async def submit_news(data: dict  ):
#     commune_chat_id = os.getenv("COMMUNE_CHAT_ID")
#     current_time    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     village         = data.get("village_name", "")
#     commune         = data.get("commune_name", "")
#     title           = data.get("title", "")
#     content         = data.get("content", "")

#     try:
#         new_entry = News(
#             village_name = village,
#             commune_name = commune,
#             title        = title,
#             content      = content,
#             created_at   = datetime.now()
#         )
#         db.add(new_entry)
#         db.commit()
#         db.refresh(new_entry)
#         print(f"✅ Recorded in DB: ID {new_entry.id}")
#     except Exception as e:
#         db.rollback() 
#         print(f"❌ Database Error: {e}")
    
#     message_text = (
#         f"📢 **មានដំណឹងក្តៅៗ មេ🔥**\n\n"
#         f"🕒 **កើតឡើងពេល:** {current_time}\n"
#         f"🏘️ **កើតឡើងនៅភូមិ:** {village}\n"
#         f"🏛️ **ក្នុងឃុំ:** {commune}\n"
#         f"📌 **ចំណងជើង:** {title}\n\n"
#         f"📝 **មាតិការ:**\n{content}"
#     )
    
#     payload = {
#         "chat_id"   : commune_chat_id,
#         "text"      : message_text,
#         "parse_mode": "Markdown"
#     }
#     v_2_c = 5 
#     c_2_d = 10
#     d_2_p = 30
#     async with httpx.AsyncClient() as client:
           
#             await asyncio.sleep(1)
#             await client.post(
#                 f"https://api.telegram.org/bot{os.getenv('COMMUNE_BOT_TOKEN')}/sendMessage",
#                 json={"chat_id": os.getenv("COMMUNE_CHAT_ID"), "text": message_text, "parse_mode": "Markdown"}
#             )
#             await asyncio.sleep(1)
#             await client.post(
#                 f"https://api.telegram.org/bot{os.getenv('DISTRICT_BOT_TOKEN')}/sendMessage",
#                 json={"chat_id": os.getenv("DISTRICT_CHAT_ID"), "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ស្រុក**\n\n{message_text}", "parse_mode": "Markdown"}
#             )
#             await asyncio.sleep(1)
#             await client.post(
#                 f"https://api.telegram.org/bot{os.getenv('PROVINCE_BOT_TOKEN')}/sendMessage",
#                 json={"chat_id": os.getenv("PROVINCE_CHAT_ID"), "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ខេត្ត**\n\n{message_text}", "parse_mode": "Markdown"}
#             )
#             return True

async def submit_news(data: dict):

    v_id = data.get("v_id")
    print(f"DEBUG: ទទួលបាន v_id ពី Frontend: {v_id}")
    
    title = data.get("title", "គ្មានចំណងជើង")
    sender = data.get("sender_name", "មិនស្គាល់អត្តសញ្ញាណ")
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
        f"📢 **មានរបាយការណ៍ថ្មីពី៖ {village_info.name_khmer}**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 **អ្នករាយការណ៍:** {sender}\n"
        f"🏘️ **ភូមិ:** {village_info.name_khmer}\n"
        f"🕒 **កាលបរិច្ឆេទ:** {current_time}\n"
        f"📌 **ចំណងជើង:** {title}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 **ខ្លឹមសារ:**\n{content}"
    )

    # async with httpx.AsyncClient() as client:
    #     try:

    #         if village_info.commune_chat_id:
    #             res_c = await client.post(
    #                 f"https://api.telegram.org/bot{village_info.bot_token}/sendMessage",
    #                 json={"chat_id": village_info.commune_chat_id, "text": message_text, "parse_mode": "Markdown"}
    #             )
    #             print(f"Telegram Commune Response: {res_c.json()}")
    #         await asyncio.sleep(1)
    #         await client.post(
    #             f"https://api.telegram.org/bot{co}/sendMessage",
    #             json={"chat_id": os.getenv("DISTRICT_CHAT_ID"), "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ស្រុក**\n\n{message_text}", "parse_mode": "Markdown"}
    #         )
    #         await asyncio.sleep(1)
    #         await client.post(
    #             f"https://api.telegram.org/bot{os.getenv('PROVINCE_BOT_TOKEN')}/sendMessage",
    #             json={"chat_id": os.getenv("PROVINCE_CHAT_ID"), "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ខេត្ត**\n\n{message_text}", "parse_mode": "Markdown"}
    #         )

    #     except Exception as telegram_err:
    #         print(f"❌ Telegram API Error: {telegram_err}")
            
    #     return True
    # async with httpx.AsyncClient() as client:
    #     try:
    #         # ១. បញ្ជូនទៅថ្នាក់ឃុំ (ប្រើ commune_chat_id ពី DB)
    #         if village_info.commune_chat_id:
    #             res_c = await client.post(
    #                 f"https://api.telegram.org/bot{village_info.bot_token}/sendMessage",
    #                 json={"chat_id": village_info.commune_chat_id, "text": message_text, "parse_mode": "Markdown"}
    #             )
    #             print(f"Telegram Commune Response: {res_c.json()}")

    #         # បង្អង់ ១ វិនាទី ដើម្បីការពារការជាប់ Block (Spam protection)
    #         await asyncio.sleep(1) 

    #         # ២. បញ្ជូនទៅថ្នាក់ស្រុក (ប្រើ district_chat_id ពី DB)
    #         if village_info.district_chat_id:
    #             res_d = await client.post(
    #                 f"https://api.telegram.org/bot{village_info.bot_token}/sendMessage",
    #                 json={
    #                     "chat_id": village_info.district_chat_id, 
    #                     "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ស្រុក**\n\n{message_text}", 
    #                     "parse_mode": "Markdown"
    #                 }
    #             )
    #             print(f"Telegram District Response: {res_d.json()}")

    #         await asyncio.sleep(1)

    #         # ៣. បញ្ជូនទៅថ្នាក់ខេត្ត (ប្រើ province_chat_id ដែលទើបនឹងបន្ថែមថ្មីក្នុង DB)
    #         if village_info.province_chat_id:
    #             res_p = await client.post(
    #                 f"https://api.telegram.org/bot{village_info.bot_token}/sendMessage",
    #                 json={
    #                     "chat_id": village_info.province_chat_id, 
    #                     "text": f"🔄 **គោរពជូនទៅ ថ្នាក់ខេត្ត**\n\n{message_text}", 
    #                     "parse_mode": "Markdown"
    #                 }
    #             )
    #             print(f"Telegram Province Response: {res_p.json()}")

    #     except Exception as telegram_err:
    #         print(f"❌ Telegram API Error: {telegram_err}")
    async with httpx.AsyncClient() as client:
        try:
            # ១. ភូមិ → ឃុំ (ប្រើ Bot ភូមិ)
            if village_info.commune_chat_id:
                res_c = await client.post(
                    f"https://api.telegram.org/bot{village_info.bot_token}/sendMessage",
                    json={"chat_id": village_info.commune_chat_id, "text": message_text, "parse_mode": "Markdown"}
                )
                print(f"Village Bot -> Commune Group: {res_c.json()}")

            await asyncio.sleep(1) 

            # ២. ឃុំ → ស្រុក (ប្រើ Bot ឃុំ - យើងអាចយក Token ពី ENV ឬ DB)
            commune_bot_token = os.getenv("COMMUNE_BOT_TOKEN") 
            
            if village_info.district_chat_id and commune_bot_token:
                res_d = await client.post(
                    f"https://api.telegram.org/bot{commune_bot_token}/sendMessage",
                    json={
                        "chat_id": village_info.district_chat_id, 
                        "text": f"🔄 **របាយការណ៍បូកសរុបពីឃុំមកថ្នាក់ស្រុក៖**\n\n{message_text}", 
                        "parse_mode": "Markdown"
                    }
                )
                print(f"Commune Bot -> District Group: {res_d.json()}")

            await asyncio.sleep(1)

            # ៣. ឃុំ → ខេត្ត (ប្រើ Bot ឃុំ ឬ Bot ស្រុក ផ្ញើបន្ត)
            if village_info.province_chat_id and commune_bot_token:
                res_p = await client.post(
                    f"https://api.telegram.org/bot{commune_bot_token}/sendMessage",
                    json={
                        "chat_id": village_info.province_chat_id, 
                        "text": f"🔄 **របាយការណ៍បូកសរុបផ្ញើជូនថ្នាក់ខេត្ត៖**\n\n{message_text}", 
                        "parse_mode": "Markdown"
                    }
                )
                print(f"Commune Bot -> Province Group: {res_p.json()}")

        except Exception as telegram_err:
            print(f"❌ Telegram API Error: {telegram_err}")
