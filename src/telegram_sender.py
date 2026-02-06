"""
Telegram Sender - 通过 Telegram Bot 发送消息

使用 Bot API: https://api.telegram.org/bot<token>/sendMessage
"""

from typing import Dict, Optional
import requests


class TelegramSender:
    """Telegram Bot 发送器"""

    def __init__(self, bot_token: str, timeout: int = 30):
        self.bot_token = bot_token
        self.timeout = timeout

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
        message_thread_id: Optional[int] = None,
    ) -> Dict:
        if not self.bot_token:
            return {"success": False, "message": "TELEGRAM_BOT_TOKEN is empty", "id": None}
        if not chat_id:
            return {"success": False, "message": "TELEGRAM_CHAT_ID is empty", "id": None}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if message_thread_id is not None:
            payload["message_thread_id"] = message_thread_id

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                return {"success": False, "message": str(data), "id": None, "response": data}
            message_id = (data.get("result") or {}).get("message_id")
            return {"success": True, "message": "sent", "id": message_id, "response": data}
        except Exception as e:
            return {"success": False, "message": str(e), "id": None}
