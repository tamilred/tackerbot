import logging
from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated, Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH, ADMIN_ID

FORCE_JOIN_CHANNEL = "MythicVoice"  # Change to your channel username without @

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client("TamilBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

async def check_force_join(client, message):
    try:
        user = await client.get_chat_member(FORCE_JOIN_CHANNEL, message.from_user.id)
        if user.status not in ["member", "administrator", "creator"]:
            invite_url = "https://t.me/+lBfth24XFCg5MTk1"
            await message.reply_text(
                "🚫 நீங்கள் முதலில் எங்கள் சேனலில் சேர வேண்டும்:

📢 https://t.me/" + FORCE_JOIN_CHANNEL,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ சேனலில் சேர", url=invite_url)],
                    [InlineKeyboardButton("🔄 மீண்டும் சரிபார்க்க", callback_data="refresh_join")]
                ])
            )
            return False
        return True
    except Exception as e:
        logger.error(f"Force join check error: {e}")
        return True  # fail-safe

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    if not await check_force_join(client, message):
        return
    await message.reply_text(
        "👋 வணக்கம்!
இந்த தமிழ் ஜாயின் டிராக்கர் போட் உங்கள் குழு மற்றும் சேனலில் உறுப்பினர்கள் சேரும் மற்றும் விலகும் செயல்பாடுகளை கண்காணிக்கிறது ✅"
    )

@app.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(_, message: Message):
    await message.reply_text(
        "**👑 நிர்வாக பக்கமும்:**

"
        "- Force Join சேனல்: @" + FORCE_JOIN_CHANNEL + "
"
        "- உங்கள் ஐடி: `" + str(ADMIN_ID) + "`
"
        "- போட்ட் செயல்பட்டுக் கொண்டு இருக்கிறது ✅",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 சேனல்", url=f"https://t.me/{FORCE_JOIN_CHANNEL}")],
            [InlineKeyboardButton("🔁 ரீஸ்டார்ட் (Manual)", callback_data="restart_bot")]
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
                    f"✅ குழுவில் சேர்ந்தார்:
👤 [{user.first_name}](tg://user?id={user.id})
📛 {update.chat.title}"
                )
            elif update.new_chat_member.status == "left":
                await client.send_message(
                    ADMIN_ID,
                    f"❌ விட்டு சென்றார்:
👤 [{user.first_name}](tg://user?id={user.id})
📛 {update.chat.title}"
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
                    f"📡 சேனலில் சேர்ந்தார்:
👤 [{user.first_name}](tg://user?id={user.id})
📛 {update.chat.title}"
                )
            elif update.new_chat_member.status == "left":
                await client.send_message(
                    ADMIN_ID,
                    f"📤 விட்டு சென்றார்:
👤 [{user.first_name}](tg://user?id={user.id})
📛 {update.chat.title}"
                )
    except Exception as e:
        logger.error(f"Channel track error: {e}")

if __name__ == "__main__":
    try:
        logger.info("Bot starting...")
        app.run()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
