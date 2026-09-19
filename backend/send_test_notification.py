"""One-off test: send a sample structured message to Telegram + email.

Uses the exact production code paths (messages.build_text / build_html) so the
delivered format is what a real poll would send. Does not touch the DB.
"""

import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app.config import load_settings
from app.notify import _send_email
from app.telegram.messages import build_html, build_text
from app.telegram.notifications import _send_message

SAMPLE_JOBS = [
    {
        "title": "Software Engineer",
        "company": "Adobe",
        "location": "Bengaluru, India",
        "url": "https://careers.adobe.com/swe",
    },
    {
        "title": "DevOps Engineer",
        "company": "Adobe",
        "location": "Bengaluru, India",
        "url": "https://careers.adobe.com/devops",
    },
    {
        "title": "Member of Technical Staff",
        "company": "Google",
        "location": "Remote",
        "url": "https://careers.google.com/mts",
    },
]


def main() -> None:
    settings = load_settings()

    text = build_text(SAMPLE_JOBS)
    print("=== TELEGRAM PREVIEW ===")
    print(text)

    if settings.telegram_enabled and settings.telegram_bot_token and settings.telegram_chat_id:
        _send_message(settings.telegram_bot_token, settings.telegram_chat_id, text)
        print("telegram: sent OK")
    else:
        print("telegram: skipped (not configured)")

    if settings.notify_enabled and settings.resend_api_key and settings.notify_to:
        html = build_html(SAMPLE_JOBS)
        _send_email(
            api_key=settings.resend_api_key,
            to_addresses=settings.notify_to,
            subject="JobQuest test — 3 sample jobs",
            html=html,
        )
        print("email: sent OK")
    else:
        print("email: skipped (not configured)")


if __name__ == "__main__":
    main()
