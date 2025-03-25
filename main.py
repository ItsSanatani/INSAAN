import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from pyrogram import Client
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputReportReasonSpam, InputReportReasonViolence, InputReportReasonChildAbuse,
    InputReportReasonPornography, InputReportReasonCopyright, InputReportReasonFake,
    InputReportReasonIllegalDrugs, InputReportReasonPersonalDetails, InputReportReasonOther
)

# 🛠 Bot और API Details
BOT_TOKEN = "7656369802:AAGdlo88cewouuiviq-eHoRHdxj_Ktji3To"
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🟢 Available Report Reasons
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

# 📂 Sessions Store
sessions = []

# 🟢 Start Command
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("🚀 Telegram Mass Reporting Bot Running!\nUse /addsession {session_string} to add accounts.")

# 🟢 Add Session
@dp.message(Command("addsession"))
async def add_session(message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("❌ Usage: `/addsession {session_string}`")
        return
    
    session_string = args[1].strip()
    sessions.append(session_string)
    await message.reply("✅ Session Added Successfully!")

# 🟢 List Sessions
@dp.message(Command("listsessions"))
async def list_sessions(message: Message):
    if not sessions:
        await message.reply("❌ No sessions added yet.")
    else:
        await message.reply(f"✅ Active Sessions: {len(sessions)}")

# 🟢 Report a User
@dp.message(Command("report"))
async def report_user(message: Message):
    args = message.text.split(" ")
    
    if len(args) < 4:
        await message.reply(
            "❌ **Usage:** `/report @username reason count`\n\n"
            "📝 **Available Reasons:**\n"
            "`spam, violence, child_abuse, pornography, copyright, fake, drugs, personal_data, other`"
        )
        return

    target_user = args[1].strip()
    reason_key = args[2].strip().lower()
    report_count = int(args[3]) if args[3].isdigit() else 1  # Default: 1 report

    if reason_key not in REPORT_REASONS:
        await message.reply("❌ Invalid reason! Use one of these:\n`" + "`, `".join(REPORT_REASONS.keys()) + "`")
        return

    reason = REPORT_REASONS[reason_key]
    total_reports = 0
    failed_count = 0

    for session_string in sessions:
        try:
            async with Client("session", api_id=API_ID, api_hash=API_HASH, session_string=session_string) as client:
                user = await client.resolve_peer(target_user)

                for _ in range(report_count):
                    await client.invoke(ReportPeer(peer=user, reason=reason, message="Automated Report"))
                    total_reports += 1

        except Exception as e:
            failed_count += 1
            print(f"⚠️ Failed: {str(e)}")

    await message.reply(
        f"✅ **Total Reports Sent:** {total_reports} 🚀\n"
        f"❌ **Failed Attempts:** {failed_count}\n"
        f"📢 **Reason Used:** `{reason_key}`"
    )

# 🟢 Start Bot
async def main():
    print("🚀 Telegram Mass Reporting Bot Started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
