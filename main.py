import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from pyrogram import Client
from aiogram.filters import Command
from aiogram.types import Message

# ✅ Replace These with Your API Details
BOT_TOKEN = "7656369802:AAGdlo88cewouuiviq-eHoRHdxj_Ktji3To"
API_ID = 28795512  # Your API ID
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # Your API Hash

# 🔥 Initialize Aiogram Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📂 Ensure sessions directory exists
if not os.path.exists("sessions"):
    os.makedirs("sessions")

# 🟢 Handler to Start Bot
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("🚀 Telegram Mass Reporting Bot is Running!\n\nUse /addsession to add a session file.")

# 🟢 Handler to Upload Session Files
@dp.message(Command("addsession"))
async def add_session(message: Message):
    await message.reply("📂 Send a .session file to add an account.")

@dp.message(lambda message: message.document and message.document.file_name.endswith(".session"))
async def save_session(message: Message):
    file_name = message.document.file_name
    session_path = os.path.join("sessions", file_name)
    
    # 🔽 Download session file
    file = await bot.get_file(message.document.file_id)
    await bot.download_file(file.file_path, session_path)

    # ✅ Confirm Upload Success
    if os.path.exists(session_path):
        await message.reply(f"✅ Session {file_name} added successfully!")
    else:
        await message.reply("❌ Failed to save the session file. Please try again.")

# 🟢 List Available Sessions
@dp.message(Command("listsessions"))
async def list_sessions(message: Message):
    session_files = os.listdir("sessions")
    if not session_files:
        await message.reply("❌ No sessions found. Add one using /addsession.")
    else:
        await message.reply(f"✅ Active Sessions:\n" + "\n".join(session_files))

# 🟢 Delete a Session File
@dp.message(Command("deletesession"))
async def delete_session(message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("❌ Usage: /deletesession session_name.session")
        return

    session_name = args[1].strip()
    session_path = os.path.join("sessions", session_name)

    if os.path.exists(session_path):
        os.remove(session_path)
        await message.reply(f"✅ Session {session_name} deleted successfully!")
    else:
        await message.reply("❌ Session file not found.")

# 🟢 Report a User
@dp.message(Command("report"))
async def report_user(message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("❌ Usage: /report @username or chat_id")
        return

    target_user = args[1].strip()

    # 📂 Load Session Files
    session_files = os.listdir("sessions")
    if not session_files:
        await message.reply("❌ No active sessions found. Please add at least one session using /addsession.")
        return

    success_count = 0
    failed_count = 0

    for session_file in session_files:
        session_path = os.path.join("sessions", session_file)
        try:
            async with Client(session_path, api_id=API_ID, api_hash=API_HASH) as client:
                await client.report_peer(target_user, types.enums.ReportReason.SPAM)
                success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"⚠️ Failed to report from {session_file}: {str(e)}")

    await message.reply(f"✅ Reports sent successfully from {success_count} accounts! ❌ {failed_count} failed.")

# 🟢 Start Bot
async def main():
    print("🚀 Telegram Mass Reporting Bot Started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
