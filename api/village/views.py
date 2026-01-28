from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException

import httpx
from sqlalchemy.orm import Session
from api.village.models import Village
from api.village import schemas
from core.db import db
import asyncio

async def submit_news(data: dict, db):
    v_id = data.get("village_id")
    v = db.query(Village).filter(Village.unique_id == v_id).first()

async def handle_start_command(chat_id: int, first_name: str, village: Village):
    # Use the token and name from the DB record
    bot_token = village.bot_token
    ui_url = f"https://html-sigma-liart.vercel.app/?chat_id={chat_id}&v_id={village.unique_id}"
    
    welcome_text = (
        f"🙏🏻 **ជម្រាបសួរ ! {first_name}!**\n\n"
        f"នេះគឺជាប៊ូតុងរាយការណ៍សម្រាប់ **{village.name_khmer}** ។\n"
        f"សូមចុចប៊ូតុងខាងក្រោមដើម្បីផ្ញើរបាយការណ៍។"
    )

    payload = {
        "chat_id": chat_id,
        "text": welcome_text,
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "🚀 បើកទម្រង់រាយការណ៍", "web_app": {"url": ui_url}}
            ]]
        }
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload)