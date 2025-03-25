import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputReportReasonSpam, InputReportReasonViolence, InputReportReasonChildAbuse,
    InputReportReasonPornography, InputReportReasonCopyright, InputReportReasonFake,
    InputReportReasonIllegalDrugs, InputReportReasonPersonalDetails, InputReportReasonOther
)

# 🔥 Report Reasons
REPORT_REASONS = {
    "spam": InputReportReasonSpam(),
    "violence": InputReportReasonViolence(),
    "child_abuse": InputReportReasonChildAbuse(),
    "pornography": InputReportReasonPornography(),
    "copyright": InputReportReasonCopyright(),
    "fake": InputReportReasonFake(),
    "drugs": InputReportReasonIllegalDrugs(),
    "personal_data": InputReportReasonPersonalDetails(),
    "other": InputReportReasonOther()
}

# ✅ Bot Details
BOT_TOKEN = "7656369802:AAGdlo88cewouuiviq-eHoRHdxj_Ktji3To"
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📂 Ensure sessions directory exists
if not os.path.exists("sessions"):
    os.makedirs("sessions")

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("🚀 **Telegram Mass Reporting Bot is Running!**\n\nUse /addsession to add a session file.")

@dp.message(Command("addsession"))
async def add_session(message: Message):
    await message.reply("📂 **Send a .session file to add an account.**")

@dp.message(lambda message: message.document and message.document.file_name.endswith(".session"))
async def save_session(message: Message):
    file_name = message.document.file_name
    session_path = os.path.join("sessions", file_name)
    file = await bot.get_file(message.document.file_id)
    await bot.download_file(file.file_path, session_path)

    if os.path.exists(session_path):
        await message.reply(f"✅ **Session {file_name} added successfully!**")
    else:
        await message.reply("❌ **Failed to save the session file. Try again.**")

@dp.message(Command("listsessions"))
async def list_sessions(message: Message):
    session_files = os.listdir("sessions")
    if not session_files:
        await message.reply("❌ **No sessions found. Add one using /addsession.**")
    else:
        await message.reply(f"✅ **Active Sessions:**\n" + "\n".join(session_files))

@dp.message(Command("deletesession"))
async def delete_session(message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("❌ **Usage:** `/deletesession session_name.session`")
        return

    session_name = args[1].strip()
    session_path = os.path.join("sessions", session_name)

    if os.path.exists(session_path):
        os.remove(session_path)
        await message.reply(f"✅ **Session {session_name} deleted successfully!**")
    else:
        await message.reply("❌ **Session file not found.**")

@dp.message(Command("report"))
async def report_user(message: Message):
    args = message.text.split(" ")
    if len(args) < 4:
        await message.reply(
            "❌ **Usage:** `/report @username reason count delay`\n\n"
            "📝 **Available Reasons:**\n"
            "`spam, violence, child_abuse, pornography, copyright, fake, drugs, personal_data, other`\n\n"
            "🔄 **Example:** `/report @baduser spam 10 3`"
        )
        return

    target_user = args[1].strip()
    reason_key = args[2].strip().lower()
    report_count = int(args[3])
    delay = int(args[4]) if len(args) > 4 else 2  # Default Delay: 2s

    if reason_key not in REPORT_REASONS:
        await message.reply("❌ **Invalid reason! Use one of these:**\n`" + "`, `".join(REPORT_REASONS.keys()) + "`")
        return

    reason = REPORT_REASONS[reason_key]
    session_files = os.listdir("sessions")
    if not session_files:
        await message.reply("❌ **No active sessions found. Add at least one session using /addsession.**")
        return

    total_reports = 0
    failed_count = 0

    for session_file in session_files:
        session_path = os.path.join("sessions", session_file)
        try:
            async with Client(session_path, api_id=API_ID, api_hash=API_HASH) as client:
                user = await client.resolve_peer(target_user)

                # 🔹 Auto-Join If Needed
                try:
                    chat = await client.get_chat(target_user)
                    if chat.type in ["channel", "supergroup"]:
                        await client.join_chat(target_user)
                        await asyncio.sleep(2)  # Wait after joining
                except Exception:
                    pass  # If join fails, continue reporting

                for _ in range(report_count):
                    try:
                        await client.invoke(ReportPeer(peer=user, reason=reason, message="Automated Report"))
                        total_reports += 1
                        await asyncio.sleep(delay)  # Delay Between Reports
                    except FloodWait as e:
                        print(f"⚠️ FloodWait: {e.value}s")
                        await asyncio.sleep(e.value)  # Wait for flood protection
                    except Exception as e:
                        print(f"⚠️ Failed from {session_file}: {str(e)}")
                        failed_count += 1

                # 🔹 Auto-Leave After Reporting
                try:
                    await client.leave_chat(target_user)
                except Exception:
                    pass  # Ignore leave errors

        except Exception as e:
            print(f"⚠️ Error in session {session_file}: {e}")
            failed_count += 1

    await message.reply(
        f"✅ **Total Reports Sent:** {total_reports} 🚀\n"
        f"❌ **Failed Attempts:** {failed_count}\n"
        f"📢 **Reason Used:** `{reason_key}`\n"
        f"⏳ **Delay Between Reports:** `{delay}s`"
    )

async def main():
    print("🚀 Telegram Mass Reporting Bot Started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
