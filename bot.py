import logging
from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated, Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH, ADMIN_ID

# Fixed invite link to your private group or channel
FIXED_INVITE_URL = "https://t.me/+lBfth24XFCg5MTk1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client("TamilBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Force join using fixed invite link
async def check_force_join(client, message):
    try:
        # Try to get membership info from chat (fallback logic)
        user = message.from_user
        member = await client.get_chat_member(message.chat.id, user.id)
        return True
    except Exception as e:
        logger.error(f"Force join check error: {e}")
        await message.reply_text(
            "🚫 நீங்கள் முதலில் எங்கள் சேனலில் சேர வேண்டும்:\n\n📢",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ சேனலில் சேர", url=FIXED_INVITE_URL)],
                [InlineKeyboardButton("🔄 மீண்டும் சரிபார்க்க", callback_data="refresh_join")]
            ])
        )
        return False

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    if not await check_force_join(client, message):
        return
    await message.reply_text("👋 வணக்கம்!\nஇந்த தமிழ் ஜாயின் டிராக்கர் போட் செயல்படுகிறது ✅")

@app.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(_, message: Message):
    await message.reply_text(
        "**👑 நிர்வாக பக்கம்:**\n\n"
        "- Invite Link மூலம் Force Join செய்கிறது ✅\n"
        "- உங்கள் ஐடி: `" + str(ADMIN_ID) + "`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 சேனல் இன்பைட்", url=FIXED_INVITE_URL)],
            [InlineKeyboardButton("🔁 ரீஸ்டார்ட்", callback_data="restart_bot")]
        ])
    )

@app.on_callback_query(filters.regex("refresh_join"))
async def refresh_join_check(client, callback_query):
    if await check_force_join(client, callback_query.message):
        await callback_query.message.delete()
        await callback_query.message.reply_text("✅ நன்றி! நீங்கள் சேனலில் சேர்ந்துள்ளீர்கள்.")

@app.on_chat_member_updated(filters.group)
async def handle_group_membership_change(client: Client, update: ChatMemberUpdated):
    try:
        user = update.new_chat_member.user
        if update.old_chat_member and update.new_chat_member and update.old_chat_member.status != update.new_chat_member.status:
            if update.new_chat_member.status == "member":
                await client.send_message(
                    ADMIN_ID,
                    f"✅ குழுவில் சேர்ந்தார்:\n👤 [{user.first_name}](tg://user?id={user.id})\n📛 {update.chat.title}"
                )
            elif update.new_chat_member.status == "left":
                await client.send_message(
                    ADMIN_ID,
                    f"❌ விட்டு சென்றார்:\n👤 [{user.first_name}](tg://user?id={user.id})\n📛 {update.chat.title}"
                )
    except Exception as e:
        logger.error(f"Group track error: {e}")

@app.on_chat_member_updated(filters.channel)
async def handle_channel_membership_change(client: Client, update: ChatMemberUpdated):
    try:
        user = update.new_chat_member.user
        if update.old_chat_member and update.new_chat_member and update.old_chat_member.status != update.new_chat_member.status:
            if update.new_chat_member.status == "member":
                await client.send_message(
                    ADMIN_ID,
                    f"📡 சேனலில் சேர்ந்தார்:\n👤 [{user.first_name}](tg://user?id={user.id})\n📛 {update.chat.title}"
                )
            elif update.new_chat_member.status == "left":
                await client.send_message(
                    ADMIN_ID,
                    f"📤 விட்டு சென்றார்:\n👤 [{user.first_name}](tg://user?id={user.id})\n📛 {update.chat.title}"
                )
    except Exception as e:
        logger.error(f"Channel track error: {e}")

if __name__ == "__main__":
    try:
        logger.info("Bot starting...")
        app.run()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
