"""
Telegram Study Reminder — IIT Bombay GenAI Program
====================================================
Uses Telegram Bot API — 100% FREE, no approval needed
Sends personalized reminders before each study session.

SETUP GUIDE (5 minutes):
--------------------------
1. Open Telegram → Search for @BotFather
2. Send: /newbot
3. Choose a name: "IIT GenAI Mentor"
4. Choose a username: "iit_genai_mentor_bot"
5. BotFather gives you a TOKEN — paste it below as BOT_TOKEN
6. Now message your new bot once (any message) to start a chat
7. Get your CHAT_ID:
   - Open: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   - Look for "chat":{"id": XXXXXXXXX} — that's your CHAT_ID
8. Paste BOT_TOKEN and CHAT_ID below
9. Run: python3 telegram_reminder.py test
10. Set up cron (see bottom) — done!

COST: FREE forever. No credit card. No approval.
"""

import requests
import datetime
import pytz
import sys
import os

# ============================================================
# 🔧 CONFIGURATION
# Works on PC (reads directly) AND GitHub Actions (reads from env secrets)
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # Set in GitHub Secrets
CHAT_ID   = os.environ.get("CHAT_ID",   "")  # Set in GitHub Secrets
IST       = pytz.timezone("Asia/Kolkata")

# ============================================================
# 📅 FULL SCHEDULE (matches your ICS calendar exactly)
# ============================================================
WEEKDAY_SCHEDULE = {
    0: [  # Monday — Theory Day
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://arxiv.org/list/cs.LG/recent",
         "tip": "Scan 3 abstracts. Pick 1 that excites you. That's today's energy."},
        {"time": "18:50", "title": "📚 Theory Deep Dive", "duration": "90 min",
         "link": "https://karpathy.ai/zero-to-hero.html",
         "tip": "Phone face down. Build concepts, not confusion. Take handwritten notes."},
        {"time": "20:20", "title": "💻 Project Coding", "duration": "60 min",
         "link": "https://github.com",
         "tip": "Push at least 1 commit tonight. Progress > perfection. Document as you go."},
    ],
    1: [  # Tuesday — Paper + LeetCode Day
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://paperswithcode.com/latest",
         "tip": "What got a new SOTA today? Note 1 surprising result."},
        {"time": "18:50", "title": "📄 Paper Deep Dive", "duration": "90 min",
         "link": "https://arxiv.org/list/cs.AI/recent",
         "tip": "Abstract → Conclusion → Figures → Full paper. Log summary in Notion."},
        {"time": "20:20", "title": "⚡ LeetCode", "duration": "60 min",
         "link": "https://leetcode.com/problemset/all/?difficulty=Medium",
         "tip": "One medium problem. Think before you code. Explain it out loud first."},
    ],
    2: [  # Wednesday — Coding + GitHub Day
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://huggingface.co/papers",
         "tip": "HuggingFace trending — what's the ML world building today?"},
        {"time": "18:50", "title": "💻 Coding + GitHub Push", "duration": "90 min",
         "link": "https://colab.research.google.com",
         "tip": "Implement something from this week's paper. Even 20 lines counts."},
        {"time": "20:20", "title": "🚀 GitHub Profile Update", "duration": "60 min",
         "link": "https://github.com",
         "tip": "Update your README. Add today's work. Recruiters check this every week."},
    ],
    3: [  # Thursday — Tools + O'Reilly Day
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://tldr.tech/ai",
         "tip": "TLDR AI newsletter — 5 min to know what the industry shipped today."},
        {"time": "18:50", "title": "📖 O'Reilly Reading", "duration": "90 min",
         "link": "https://learning.oreilly.com",
         "tip": "Code every example. Don't read passively — type it and run it in Colab."},
        {"time": "20:20", "title": "🛠️ AI Tools Exploration", "duration": "60 min",
         "link": "https://huggingface.co/spaces",
         "tip": "Try one new HuggingFace Space. Understand HOW it works, not just THAT it works."},
    ],
    4: [  # Friday — Job Search + Review Day
        {"time": "05:50", "title": "🌅 AI Morning Brief", "duration": "30 min",
         "link": "https://www.linkedin.com/jobs/search/?keywords=AI+Engineer+India",
         "tip": "Check 3 job postings. Note 1 skill gap. That's your weekend focus."},
        {"time": "18:50", "title": "💼 Job Search + Applications", "duration": "90 min",
         "link": "https://wellfound.com/jobs",
         "tip": "Apply to 2 companies. Quality > quantity. Customize every message."},
        {"time": "20:20", "title": "📝 Weekly Review + LinkedIn Post", "duration": "60 min",
         "link": "https://linkedin.com",
         "tip": "Write your Friday learning post. What did you master this week? Share it publicly."},
    ],
}

WEEKEND_SCHEDULE = {
    5: [  # Saturday
        {"time": "05:50", "title": "🐍 Python Practice", "duration": "90 min",
         "link": "https://colab.research.google.com",
         "tip": "30 min solo coding, then use AI to review. Push to GitHub when done."},
        {"time": "07:20", "title": "📚 O'Reilly Reading", "duration": "90 min",
         "link": "https://learning.oreilly.com",
         "tip": "Deep read. Highlights + Anki cards. Build your personal knowledge base."},
        {"time": "09:50", "title": "🎓 IIT Bombay Live Class", "duration": "180 min",
         "link": "https://nptel.ac.in",
         "tip": "Take notes by hand. Ask at least 1 question. Passive listening = wasted time."},
        {"time": "15:50", "title": "📄 Paper Reading", "duration": "120 min",
         "link": "https://arxiv.org/list/cs.LG/recent",
         "tip": "Abstract → Conclusion → Figures → Full. Log in Notion. 3-sentence summary minimum."},
        {"time": "18:20", "title": "🔁 Revision + Coding", "duration": "90 min",
         "link": "https://colab.research.google.com",
         "tip": "Implement the paper's key idea. Even a toy version. Commit it."},
    ],
    6: [  # Sunday
        {"time": "09:50", "title": "🚀 Project Work", "duration": "180 min",
         "link": "https://github.com",
         "tip": "Ship the milestone. Done > perfect. Push and document every step."},
        {"time": "13:50", "title": "💼 LinkedIn + Portfolio", "duration": "60 min",
         "link": "https://linkedin.com",
         "tip": "Update your profile. Add this week's project. Connect with 3 AI people."},
        {"time": "15:20", "title": "🔍 Job Search", "duration": "90 min",
         "link": "https://wellfound.com/jobs",
         "tip": "3 startup applications on AngelList/Wellfound. Startups move faster than big tech."},
        {"time": "17:20", "title": "📋 Weekly Review", "duration": "60 min",
         "link": "https://notion.so",
         "tip": "Log everything in Notion. What worked? What didn't? Set 3 goals for next week."},
    ],
}

ALL_SCHEDULE = {**WEEKDAY_SCHEDULE, **WEEKEND_SCHEDULE}

# ============================================================
# 📊 WEEK CALCULATOR
# ============================================================
def get_current_week() -> int:
    start_date = datetime.date(2026, 3, 28)
    today = datetime.date.today()
    delta = (today - start_date).days
    if delta < 0:
        return 0
    return min((delta // 7) + 1, 22)

# ============================================================
# 💬 MESSAGE BUILDER
# ============================================================
def build_message(session: dict, minutes_until: int) -> str:
    now = datetime.datetime.now(IST)
    day_name = now.strftime("%A")
    week_num = get_current_week()

    week_label = f"Week {week_num}/22" if week_num > 0 else "Starting Soon"

    msg = (
        f"⏰ *{minutes_until} min to go!*\n"
        f"\n"
        f"*{session['title']}*\n"
        f"📅 {day_name} · {week_label}\n"
        f"⏱ Duration: {session['duration']}\n"
        f"\n"
        f"🔗 [Open now]({session['link']})\n"
        f"\n"
        f"💡 *Mentor tip:*\n"
        f"_{session['tip']}_\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"_IIT Bombay GenAI Program_"
    )
    return msg

# ============================================================
# 📤 SEND TELEGRAM MESSAGE
# ============================================================
def send_telegram_message(message: str) -> dict:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    response = requests.post(url, json=payload)
    return response.json()

# ============================================================
# 🕐 MAIN CHECKER — Run this every minute via cron
# ============================================================
def check_and_remind(reminder_minutes: int = 10):
    now = datetime.datetime.now(IST)
    current_weekday = now.weekday()
    current_time_str = now.strftime("%H:%M")

    schedule_today = ALL_SCHEDULE.get(current_weekday, [])

    for session in schedule_today:
        session_hour, session_min = map(int, session["time"].split(":"))
        session_dt = now.replace(hour=session_hour, minute=session_min, second=0, microsecond=0)
        time_diff_minutes = (session_dt - now).total_seconds() / 60

        if 8 <= time_diff_minutes <= 12:
            message = build_message(session, reminder_minutes)
            result = send_telegram_message(message)
            print(f"[{current_time_str}] ✅ Sent: {session['title']}")
            print(f"API: {result}")
            return

    print(f"[{current_time_str}] No sessions in ~{reminder_minutes} min.")

# ============================================================
# 🧪 TEST — Sends a message right now to verify setup
# ============================================================
def send_test_message():
    week = get_current_week()
    msg = (
        "✅ *Telegram Reminder Bot Active!*\n"
        "\n"
        "Your IIT Bombay GenAI study reminders are now set up.\n"
        "\n"
        f"📅 Program Status: Week {week} of 22\n"
        "⏰ You'll get a message 10 min before each session\n"
        "📚 Sessions: 14/week × 22 weeks = 308 total\n"
        "\n"
        "🎯 *Stay consistent. Stay curious.*\n"
        "\n"
        "━━━━━━━━━━━━━━━━━\n"
        "_IIT Bombay GenAI Program — Sandeep 2026_"
    )
    result = send_telegram_message(msg)
    print("Test message sent!")
    print(f"Response: {result}")

# ============================================================
# 📅 DAILY AGENDA — Send full day schedule each morning
# ============================================================
def send_daily_agenda():
    now = datetime.datetime.now(IST)
    weekday = now.weekday()
    day_name = now.strftime("%A, %d %B")
    week_num = get_current_week()
    sessions = ALL_SCHEDULE.get(weekday, [])

    if not sessions:
        return

    lines = [
        f"🗓 *Today's Schedule — {day_name}*",
        f"📍 Week {week_num}/22 · IIT Bombay GenAI",
        "━━━━━━━━━━━━━━━━━",
        ""
    ]
    for i, s in enumerate(sessions, 1):
        lines.append(f"*{i}. {s['time']} — {s['title']}*")
        lines.append(f"   ⏱ {s['duration']}")
        lines.append(f"   🔗 [Open]({s['link']})")
        lines.append("")

    lines += [
        "━━━━━━━━━━━━━━━━━",
        f"_Total: {len(sessions)} sessions today_",
        "_Make every one count. 🔥_"
    ]

    result = send_telegram_message("\n".join(lines))
    print(f"Daily agenda sent for {day_name}")
    print(f"Response: {result}")

# ============================================================
# CRON SETUP:
#
# Open terminal and run:   crontab -e
# Add these 2 lines:
#
# Every minute — check for upcoming sessions (10 min reminder):
# * * * * * /usr/bin/python3 /path/to/telegram_reminder.py >> /tmp/tg_reminder.log 2>&1
#
# Every morning at 6:00 AM — send full day agenda:
# 0 6 * * * /usr/bin/python3 /path/to/telegram_reminder.py agenda >> /tmp/tg_reminder.log 2>&1
#
# Replace /path/to/ with your actual file path.
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            send_test_message()
        elif sys.argv[1] == "agenda":
            send_daily_agenda()
    else:
        check_and_remind(reminder_minutes=10)
