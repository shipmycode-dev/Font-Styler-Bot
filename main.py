# main.py
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from style import apply_style, get_total_styles

# ================= DUMMY WEB SERVER FOR RENDER/KOYEB =================
class WebUIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Aacha UI wala HTML (Modern Dark Theme)
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Font Styler Bot - Status</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #0f172a;
                    color: #f8fafc;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }
                .card {
                    background: #1e293b;
                    padding: 40px;
                    border-radius: 16px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    border: 1px solid #334155;
                    max-width: 400px;
                    width: 90%;
                }
                h1 { color: #38bdf8; margin-bottom: 10px; font-size: 28px; }
                p { font-size: 16px; color: #cbd5e1; margin-bottom: 30px; }
                .status-badge {
                    display: inline-block;
                    padding: 12px 24px;
                    background: rgba(16, 185, 129, 0.1);
                    color: #10b981;
                    border: 1px solid #10b981;
                    border-radius: 30px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
                    70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🤖 Font Styler Bot</h1>
                <p>Your Telegram Bot is successfully deployed and running 24/7 without interruptions.</p>
                <div class="status-badge">🟢 BOT IS LIVE</div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

    # Disable default console logging for every ping to keep logs clean
    def log_message(self, format, *args):
        pass

def keep_alive():
    # Render aur Koyeb automatically $PORT variable dete hain
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), WebUIHandler)
    server.serve_forever()

# Start the web server in a background thread
threading.Thread(target=keep_alive, daemon=True).start()


# ================= ENVIRONMENT VARIABLES =================
API_ID = int(os.environ.get('API_ID', '32541562')) 
API_HASH = os.environ.get('API_HASH', 'e37e4432298d5a5eb4a6e32c18804283') 
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8813217868:AAFplgrX7Kie_rzursBp1u689UJW5GyhsJ0')

# ================= CONSTANTS & MEDIA =================
IMG_URL = "https://cdn.pixabay.com/photo/2024/09/22/23/01/ai-generated-9067131_640.jpg" 
ITEMS_PER_PAGE = 10 
USER_SESSIONS = {}

app = Client("FontStylerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= HANDLERS =================

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    welcome_text = (
        "**👋 Hello Buddy! Welcome to the Advance Font Styler Bot.**\n\n"
        "Main tumhare normal boring text ko 50+ Premium Fonts me convert kar sakta hu.\n\n"
        "**How to use:**\n"
        "Just type `/f Your Text Here`\n\n"
        "👇 _Click the buttons below for more info._"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤖 About", callback_data="about_bot"),
            InlineKeyboardButton("🆘 Help", callback_data="help_bot")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/yourusername")
        ]
    ])
    
    await message.reply_photo(
        photo=IMG_URL,
        caption=welcome_text,
        reply_markup=keyboard
    )

@app.on_message(filters.command("f") & filters.private)
async def font_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Format Error!**\nSahi format use karo:\n`/f Tumhara Text`")
        
    user_text = message.text.split(None, 1)[1]
    user_id = message.from_user.id
    
    USER_SESSIONS[user_id] = user_text
    
    await show_fonts_page(message, user_text, page=0)

# ================= CALLBACK QUERIES =================

@app.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    if data == "about_bot":
        text = "**🤖 About This Bot:**\n\n• **Language:** Python 3\n• **Library:** Pyrogram\n• **Host:** Cloud Server\n\n_Fast and advance font styler built for creators!_"
        await query.answer()
        await query.message.edit_caption(caption=text, reply_markup=get_back_keyboard("start_menu"))
        
    elif data == "help_bot":
        text = "**🆘 Help Menu:**\n\n1. Type `/f` followed by your text.\n_Example: `/f Hello World`_\n2. Bot tumhein buttons ke form me fonts dega.\n3. Jo font pasand aaye us button pe tap karo.\n4. Bot ek Message bhejega jise tap karte hi wo COPY ho jayega."
        await query.answer()
        await query.message.edit_caption(caption=text, reply_markup=get_back_keyboard("start_menu"))
        
    elif data == "start_menu":
        welcome_text = "**👋 Hello Buddy! Welcome to the Advance Font Styler Bot.**\n\nJust type `/f Your Text Here`"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 About", callback_data="about_bot"), InlineKeyboardButton("🆘 Help", callback_data="help_bot")]
        ])
        await query.answer()
        await query.message.edit_caption(caption=welcome_text, reply_markup=keyboard)
        
    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        if user_id not in USER_SESSIONS:
            return await query.answer("Session expired. Please send `/f text` again.", show_alert=True)
            
        text = USER_SESSIONS[user_id]
        await query.answer()
        await edit_fonts_page(query.message, text, page)
        
    elif data.startswith("copy_"):
        style_idx = int(data.split("_")[1])
        if user_id not in USER_SESSIONS:
            return await query.answer("Session expired. Please send `/f text` again.", show_alert=True)
            
        original_text = USER_SESSIONS[user_id]
        styled_text = apply_style(original_text, style_idx)
        
        copy_msg = f"**✨ Style Applied! Tap text below to copy:**\n\n`{styled_text}`"
        
        await query.answer("Style Generated!", show_alert=False)
        await client.send_message(user_id, copy_msg)


# ================= PAGINATION LOGIC =================

def get_back_keyboard(callback_data: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=callback_data)]])

async def show_fonts_page(message: Message, text: str, page: int):
    keyboard = build_fonts_keyboard(text, page)
    await message.reply_text(
        f"**🎨 Choose a Font Style:**\n\n_Your Text:_ `{text}`\n_Page:_ {page + 1}",
        reply_markup=keyboard
    )

async def edit_fonts_page(message: Message, text: str, page: int):
    keyboard = build_fonts_keyboard(text, page)
    await message.edit_text(
        f"**🎨 Choose a Font Style:**\n\n_Your Text:_ `{text}`\n_Page:_ {page + 1}",
        reply_markup=keyboard
    )

def build_fonts_keyboard(text: str, page: int):
    total_styles = get_total_styles()
    total_pages = (total_styles + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_styles)
    
    buttons = []
    
    for i in range(start_idx, end_idx):
        preview_text = apply_style(text[:15] + ".." if len(text) > 15 else text, i)
        buttons.append([InlineKeyboardButton(preview_text, callback_data=f"copy_{i}")])
        
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Pre", callback_data=f"page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
        
    buttons.append(nav_buttons)
    return InlineKeyboardMarkup(buttons)

if __name__ == "__main__":
    # Custom ASCII Art Print
    ascii_art = r"""
  ____  _       _                            
 / ___|| |_   _| | ___ _ __   /\/\   ___   _ 
 \___ \| | | | | |/ _ \ '__| /    \ / _ \ (_)
  ___) | | |_| | |  __/ |   / /\/\ \  __/  _ 
 |____/|_|\__, |_|\___|_|   \/    \/\___| (_)
          |___/                              
    """
    print(ascii_art)
    print("🚀 Web server started! Bot is live and connecting to Telegram...")
    app.run()
