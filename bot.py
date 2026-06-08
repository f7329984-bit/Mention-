import asyncio
import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import threading

#=============== CONFIG ================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")

#=============== SIMPLE HTTP SERVER FOR RENDER ================
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Mention Bot is running!")
        
        def log_message(self, format, *args):
            pass
    
    def run_server():
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), Handler)
        server.serve_forever()
    
    threading.Thread(target=run_server, daemon=True).start()
    print("✅ Web server started for Render")
except Exception as e:
    print(f"⚠️ Web server skipped: {e}")

#=============== BOT INIT ================
app = Client("mention_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

tagging_active = {}
current_tasks = {}

#=============== MENTION FUNCTIONS (keep as they are) ================
async def mention_all_members(client, chat_id, message_text, chat_title):
    global tagging_active
    
    try:
        members = []
        async for member in client.get_chat_members(chat_id, limit=500):
            if member.user and not member.user.is_bot:
                members.append(member.user)
        
        if not members:
            await client.send_message(chat_id, "❌ No members found!")
            tagging_active[chat_id] = False
            return
        
        total = len(members)
        await client.send_message(chat_id, f"📊 Found {total} members. Starting tag...")
        
        chunk_size = 15
        tagged = 0
        
        for i in range(0, len(members), chunk_size):
            if not tagging_active.get(chat_id, False):
                await client.send_message(chat_id, f"🛑 Tagging stopped! Tagged {tagged}/{total} members.")
                return
            
            chunk = members[i:i+chunk_size]
            mentions = []
            
            for member in chunk:
                if member.username:
                    mentions.append(f"@{member.username}")
                else:
                    mentions.append(member.first_name)
            
            tag_msg = f"{message_text}\n\n" + "\n".join(mentions)
            
            try:
                await client.send_message(chat_id, tag_msg)
                tagged += len(chunk)
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(5)
        
        if tagging_active.get(chat_id, False):
            await client.send_message(chat_id, f"✅ Tagging completed! Tagged {tagged}/{total} members.")
        
        tagging_active[chat_id] = False
        
    except Exception as e:
        await client.send_message(chat_id, f"❌ Error: {str(e)[:100]}")
        tagging_active[chat_id] = False

async def mention_admins_only(client, chat_id, message_text, chat_title):
    global tagging_active
    
    try:
        admins = []
        async for member in client.get_chat_members(chat_id, filter="administrators"):
            if member.user and not member.user.is_bot:
                admins.append(member.user)
        
        if not admins:
            await client.send_message(chat_id, "❌ No admins found!")
            tagging_active[chat_id] = False
            return
        
        total = len(admins)
        await client.send_message(chat_id, f"📊 Found {total} admins. Tagging admins...")
        
        chunk_size = 15
        tagged = 0
        
        for i in range(0, len(admins), chunk_size):
            if not tagging_active.get(chat_id, False):
                await client.send_message(chat_id, f"🛑 Tagging stopped! Tagged {tagged}/{total} admins.")
                return
            
            chunk = admins[i:i+chunk_size]
            mentions = []
            
            for admin in chunk:
                if admin.username:
                    mentions.append(f"@{admin.username}")
                else:
                    mentions.append(admin.first_name)
            
            tag_msg = f"👑 {message_text}\n\n" + "\n".join(mentions)
            
            try:
                await client.send_message(chat_id, tag_msg)
                tagged += len(chunk)
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(5)
        
        if tagging_active.get(chat_id, False):
            await client.send_message(chat_id, f"✅ Admin tagging completed! Tagged {tagged}/{total} admins.")
        
        tagging_active[chat_id] = False
        
    except Exception as e:
        await client.send_message(chat_id, f"❌ Error: {str(e)[:100]}")
        tagging_active[chat_id] = False

async def mention_members_only(client, chat_id, message_text, chat_title):
    global tagging_active
    
    try:
        admin_ids = set()
        async for member in client.get_chat_members(chat_id, filter="administrators"):
            if member.user and not member.user.is_bot:
                admin_ids.add(member.user.id)
        
        members = []
        async for member in client.get_chat_members(chat_id, limit=500):
            if member.user and not member.user.is_bot and member.user.id not in admin_ids:
                members.append(member.user)
        
        if not members:
            await client.send_message(chat_id, "❌ No normal members found!")
            tagging_active[chat_id] = False
            return
        
        total = len(members)
        await client.send_message(chat_id, f"📊 Found {total} members (excluding admins)...")
        
        chunk_size = 15
        tagged = 0
        
        for i in range(0, len(members), chunk_size):
            if not tagging_active.get(chat_id, False):
                await client.send_message(chat_id, f"🛑 Tagging stopped! Tagged {tagged}/{total} members.")
                return
            
            chunk = members[i:i+chunk_size]
            mentions = []
            
            for member in chunk:
                if member.username:
                    mentions.append(f"@{member.username}")
                else:
                    mentions.append(member.first_name)
            
            tag_msg = f"📢 {message_text}\n\n" + "\n".join(mentions)
            
            try:
                await client.send_message(chat_id, tag_msg)
                tagged += len(chunk)
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(5)
        
        if tagging_active.get(chat_id, False):
            await client.send_message(chat_id, f"✅ Tagging completed! Tagged {tagged}/{total} members.")
        
        tagging_active[chat_id] = False
        
    except Exception as e:
        await client.send_message(chat_id, f"❌ Error: {str(e)[:100]}")
        tagging_active[chat_id] = False

#=============== COMMANDS ================
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user = message.from_user
    await message.reply_text(
        f"🔥 Welcome {user.first_name}! 🔥\n\n"
        f"**Mention Bot**\n\n"
        f"• /tagall <msg> - Tag all members\n"
        f"• /tagadmins <msg> - Tag admins\n"
        f"• /tagmembers <msg> - Tag members\n"
        f"• /stop - Stop tagging\n\n"
        f"Made by @ll_SUPRRME_XD_ll"
    )

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
🤖 **MENTION BOT**

/tagall <message> - Tag all members
/tagadmins <message> - Tag only admins
/tagmembers <message> - Tag only members
/stop - Stop tagging
/status - Check status

Example:
/tagall Hello everyone!

Note: Bot must be ADMIN in group!
    """
    await message.reply_text(help_text)

@app.on_message(filters.command("tagall") & filters.group)
async def tag_all_command(client, message: Message):
    global tagging_active, current_tasks
    
    chat_id = message.chat.id
    
    if tagging_active.get(chat_id, False):
        await message.reply_text("⚠️ Tagging already in progress! Use /stop to stop.")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text("❌ Usage: `/tagall Your message here`")
        return
    
    msg_text = parts[1]
    chat_title = message.chat.title
    
    tagging_active[chat_id] = True
    
    await message.reply_text(f"🚀 TAGGING ALL MEMBERS!\n📝 {msg_text}\n\nUse /stop to stop.")
    await message.delete()
    
    task = asyncio.create_task(mention_all_members(client, chat_id, msg_text, chat_title))
    current_tasks[chat_id] = task

@app.on_message(filters.command("tagadmins") & filters.group)
async def tag_admins_command(client, message: Message):
    global tagging_active, current_tasks
    
    chat_id = message.chat.id
    
    if tagging_active.get(chat_id, False):
        await message.reply_text("⚠️ Tagging already in progress!")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text("❌ Usage: `/tagadmins Your message here`")
        return
    
    msg_text = parts[1]
    chat_title = message.chat.title
    
    tagging_active[chat_id] = True
    
    await message.reply_text(f"👑 TAGGING ADMINS!\n📝 {msg_text}")
    await message.delete()
    
    task = asyncio.create_task(mention_admins_only(client, chat_id, msg_text, chat_title))
    current_tasks[chat_id] = task

@app.on_message(filters.command("tagmembers") & filters.group)
async def tag_members_command(client, message: Message):
    global tagging_active, current_tasks
    
    chat_id = message.chat.id
    
    if tagging_active.get(chat_id, False):
        await message.reply_text("⚠️ Tagging already in progress!")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text("❌ Usage: `/tagmembers Your message here`")
        return
    
    msg_text = parts[1]
    chat_title = message.chat.title
    
    tagging_active[chat_id] = True
    
    await message.reply_text(f"📢 TAGGING MEMBERS!\n📝 {msg_text}")
    await message.delete()
    
    task = asyncio.create_task(mention_members_only(client, chat_id, msg_text, chat_title))
    current_tasks[chat_id] = task

@app.on_message(filters.command("stop") & filters.group)
async def stop_command(client, message: Message):
    global tagging_active, current_tasks
    
    chat_id = message.chat.id
    
    if tagging_active.get(chat_id, False):
        tagging_active[chat_id] = False
        if chat_id in current_tasks:
            current_tasks[chat_id].cancel()
        await message.reply_text("🛑 Tagging stopped!")
    else:
        await message.reply_text("⚠️ No active tagging!")
    
    await message.delete()

@app.on_message(filters.command("status"))
async def status_command(client, message: Message):
    chat_id = message.chat.id if message.chat else None
    status = "🟢 Active" if tagging_active.get(chat_id, False) else "⚪ Idle"
    await message.reply_text(f"📊 Status: {status}\n✅ Bot is ready!")

#=============== MAIN ================
def main():
    if not API_ID or not API_HASH or not BOT_TOKEN:
        print("❌ Please set API_ID, API_HASH, BOT_TOKEN!")
        return
    
    print("=" * 50)
    print("🤖 MENTION BOT STARTED!")
    print("=" * 50)
    print("Commands: /tagall, /tagadmins, /tagmembers, /stop")
    print("=" * 50)
    
    app.run()

if __name__ == "__main__":
    main()
