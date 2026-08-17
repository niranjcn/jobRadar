"""Telegram notification channel and command bot.

- messages.py       — shared structured message builders (Telegram + email)
- notifications.py  — outbound alert sender (send_telegram_notifications)
- bot.py            — command menu + long-polling command bot
"""

from app.telegram.messages import (
    build_html,
    build_text,
    build_text_sections,
    build_text_summary,
    group_by_company,
)
from app.telegram.notifications import send_telegram_notifications

__all__ = [
    "build_html",
    "build_text",
    "build_text_sections",
    "build_text_summary",
    "group_by_company",
    "send_telegram_notifications",
]
