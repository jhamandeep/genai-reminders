"""
WhatsApp Study Reminder — IIT Bombay GenAI Program
====================================================
Uses WhatsApp Business Cloud API (Meta) — FREE tier
Sends you a personalized reminder before each study session.

SETUP GUIDE (one-time, ~15 minutes):
--------------------------------------
1. Go to https://developers.facebook.com/
2. Create a new App → Business → Add "WhatsApp" product
3. Go to WhatsApp > API Setup
4. Note your:
   - PHONE_NUMBER_ID (shown in API Setup)
   - ACCESS_TOKEN (temporary token shown, or generate permanent one)
   - YOUR_WHATSAPP_NUMBER (your number in format: 91XXXXXXXXXX for India)
5. Send a test message to verify setup
6. Schedule this script with cron (see bottom of file)

COST: FREE — Meta gives 1000 free conversations/month
"""

import requests
import json
import datetime
import pytz
import os

# ============================================================
# 🔧 CONFIGURATION — Fill these in
# ============================================================
PHONE_NUMBER_ID = os.environ.get("WA_PHONE_ID", "")
ACCESS_TOKEN    = os.environ.get("WA_TOKEN",    "")
TO_NUMBER       = "919625701988"              # Your WhatsApp number (no +, no spaces)
IST             = pytz.timezone("Asia/Kolkata")

# ============================================================
# 📅 SCHEDULE — Your daily sessions (matches your ICS calendar)
# ============================================================
WEEKDAY_SCHEDULE = {
    0: [  # Monday
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://arxiv.org/list/cs.LG/recent",
         "tip": "Scan 3 abstracts. Pick 1 that excites you. That's today's energy."},
        {"time": "18:50", "title": "📚 Theory Deep Dive", "duration": "90 min",
         "link": "https://karpathy.ai/zero-to-hero.html",
         "tip": "No distractions. Phone face down. Build concepts, not confusion."},
        {"time": "20:20", "title": "💻 Project Coding", "duration": "60 min",
         "link": "https://github.com",
         "tip": "Push at least 1 commit tonight. Progress > perfection."},
    ],
    1: [  # Tuesday
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://paperswithcode.com/latest",
         "tip": "Check Papers With Code — what got a new SOTA today?"},
        {"time": "18:50", "title": "📄 Paper Deep Dive", "duration": "90 min",
         "link": "https://arxiv.org/list/cs.AI/recent",
         "tip": "Read abstract + conclusion first. Then figures. Then full paper."},
        {"time": "20:20", "title": "⚡ LeetCode", "duration": "60 min",
         "link": "https://leetcode.com/problemset/all/?difficulty=Medium",
         "tip": "One medium problem. Think before you code. Explain it out loud."},
    ],
    2: [  # Wednesday
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://huggingface.co/papers",
         "tip": "HuggingFace trending papers — what's the ML world building today?"},
        {"time": "18:50", "title": "💻 Coding + GitHub Push", "duration": "90 min",
         "link": "https://colab.research.google.com",
         "tip": "Implement something from this week's paper. Even 20 lines counts."},
        {"time": "20:20", "title": "🚀 GitHub Profile Update", "duration": "60 min",
         "link": "https://github.com",
         "tip": "Update your README. Add today's work. Recruiters check this."},
    ],
    3: [  # Thursday
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://tldr.tech/ai",
         "tip": "TLDR AI newsletter — 5 min to know what the industry is doing."},
        {"time": "18:50", "title": "📖 O'Reilly Reading", "duration": "90 min",
         "link": "https://learning.oreilly.com",
         "tip": "Code every example. Don't read passively — type it and run it."},
        {"time": "20:20", "title": "🛠️ AI Tools Exploration", "duration": "60 min",
         "link": "https://huggingface.co/spaces",
         "tip": "Try one new HuggingFace Space. Understand HOW it works, not just THAT it works."},
    ],
    4: [  # Friday
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://www.linkedin.com/jobs/search/?keywords=AI+Engineer",
         "tip": "Check 3 job postings. Note skills you're missing. That's your weekend focus."},
        {"time": "18:50", "title": "💼 Job Search + Applications", "duration": "90 min",
         "link": "https://linkedin.com/jobs",
         "tip": "Apply to 2 companies today. Quality > quantity. Customize each message."},
        {"time": "20:20", "title": "📝 Weekly Review + LinkedIn Post", "duration": "60 min",
         "link": "https://linkedin.com",
         "tip": "Write your Friday learning post. What did you master this week? Share it."},
    ],
}

WEEKEND_SCHEDULE = {
    5: [  # Saturday
        {"time": "05:50", "title": "🐍 Python Practice", "duration": "90 min",
         "link": "https://colab.research.google.com",
         "tip": "30 min solo coding, then use AI to review. Push to GitHub."},
        {"time": "07:20", "title": "📚 O'Reilly Reading", "duration": "90 min",
         "link": "https://learning.oreilly.com",
         "tip": "Deep read. Highlights + Anki cards. Build your knowledge base."},
        {"time": "09:50", "title": "🎓 IIT Bombay Live Class", "duration": "180 min",
         "link": "https://nptel.ac.in",
         "tip": "Take notes by hand. Questions > passive listening."},
        {"time": "15:50", "title": "📄 Paper Reading", "duration": "120 min",
         "link": "https://arxiv.org/list/cs.LG/recent",
         "tip": "Abstract → Conclusion → Figures → Full paper. Log in Notion."},
        {"time": "18:20", "title": "🔁 Revision + Coding", "duration": "90 min",
         "link": "https://colab.research.google.com",
         "tip": "Implement the paper's key idea. Even a toy version."},
    ],
    6: [  # Sunday
        {"time": "09:50", "title": "🚀 Project Work", "duration": "180 min",
         "link": "https://github.com",
         "tip": "Ship the milestone. Done > perfect. Push and document."},
        {"time": "13:50", "title": "💼 LinkedIn + Portfolio", "duration": "60 min",
         "link": "https://linkedin.com",
         "tip": "Update your profile. Add this week's project. Connect with 3 people."},
        {"time": "15:20", "title": "🔍 Job Search", "duration": "90 min",
         "link": "https://wellfound.com/jobs",
         "tip": "Apply to 3 startups on AngelList/Wellfound. Startups move faster."},
        {"time": "17:20", "title": "📋 Weekly Review", "duration": "60 min",
         "link": "https://notion.so",
         "tip": "Log everything in Notion. What worked? What didn't? Plan next week."},
    ],
}

ALL_SCHEDULE = {**WEEKDAY_SCHEDULE, **WEEKEND_SCHEDULE}

# ============================================================
# 💬 MESSAGE BUILDER
# ============================================================
def build_message(session: dict, minutes_until: int) -> str:
    """Build a personalized WhatsApp reminder message."""
    now = datetime.datetime.now(IST)
    day_name = now.strftime("%A")
    week_num = get_current_week()

    lines = [
        f"⏰ *Reminder — {minutes_until} min to go!*",
        f"",
        f"*{session['title']}*",
        f"📅 {day_name} | Week {week_num} of 22",
        f"⏱️ Duration: {session['duration']}",
        f"",
        f"🔗 Open now: {session['link']}",
        f"",
        f"💡 *Mentor tip:* {session['tip']}",
        f"",
        f"_— Your AI Mentor | IIT Bombay GenAI Program_"
    ]
    return "\n".join(lines)

def get_current_week() -> int:
    """Calculate which week of the program we're in (starts Mar 28, 2026)."""
    start_date = datetime.date(2026, 3, 28)
    today = datetime.date.today()
    delta = (today - start_date).days
    if delta < 0:
        return 0
    week = (delta // 7) + 1
    return min(week, 22)

# ============================================================
# 📤 SEND MESSAGE
# ============================================================
def send_whatsapp_message(message: str) -> dict:
    """Send a WhatsApp message via Meta Cloud API."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": TO_NUMBER,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# ============================================================
# 🕐 MAIN — Check if any session starts in ~10 minutes
# ============================================================
def check_and_remind(reminder_minutes: int = 10):
    """Check current time and send reminder if a session starts soon."""
    now = datetime.datetime.now(IST)
    current_weekday = now.weekday()  # 0=Mon, 6=Sun
    current_time = now.strftime("%H:%M")

    schedule_today = ALL_SCHEDULE.get(current_weekday, [])

    for session in schedule_today:
        session_dt = datetime.datetime.strptime(session["time"], "%H:%M").replace(
            year=now.year, month=now.month, day=now.day,
            tzinfo=IST
        )
        time_diff = (session_dt - now).total_seconds() / 60

        # Send reminder if session starts in 8-12 minutes (10 min window ±2 min buffer)
        if 8 <= time_diff <= 12:
            message = build_message(session, reminder_minutes)
            result = send_whatsapp_message(message)
            print(f"[{current_time}] Sent reminder for: {session['title']}")
            print(f"API response: {result}")
            return

    print(f"[{current_time}] No sessions starting in ~{reminder_minutes} min. All good.")

# ============================================================
# 🧪 TEST MODE — Send a test message right now
# ============================================================
def send_test_message():
    """Send a test message to verify your setup works."""
    test_msg = (
        "✅ *WhatsApp Reminder Setup Successful!*\n\n"
        "Your IIT Bombay GenAI study reminders are now active.\n\n"
        "You'll receive a reminder 10 minutes before each session.\n\n"
        "🎯 22 weeks. 638 sessions. Let's go, Sandeep!\n\n"
        "_— Your AI Mentor_"
    )
    result = send_whatsapp_message(test_msg)
    print("Test message sent!")
    print(f"Response: {result}")

# ============================================================
# CRON SETUP (paste this in terminal):
# Run every minute to check for upcoming sessions:
#   crontab -e
#   Add this line:
#   * * * * * /usr/bin/python3 /path/to/whatsapp_reminder.py >> /tmp/reminder_log.txt 2>&1
#
# Or run manually for a one-time check:
#   python3 whatsapp_reminder.py
#
# To test your setup first:
#   python3 whatsapp_reminder.py test
# ============================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        send_test_message()
    else:
        check_and_remind(reminder_minutes=10)
