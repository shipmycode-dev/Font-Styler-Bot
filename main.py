# main.py
import os
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from style import apply_style, get_total_styles

class WebUIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Font Styler Bot - Status</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
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
                    border-radius: 12px;
                    border: 1px solid #334155;
                }
                h1 { color: #38bdf8; }
                .badge {
                    display: inline-block;
                    padding: 10px 20px;
                    background: rgba(16, 185, 129, 0.1);
                    color: #10b981;
                    border: 1px solid #10b981;
                    border-radius: 20px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Font Styler Bot</h1>
                <p>Telegram bot is running successfully.</p>
                <div class="badge">BOT IS LIVE</div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

    def log_message(self, format, *args):
        pass

def keep_alive():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), WebUIHandler)
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

API_ID = int(os.environ.get('API_ID', '32541562')) 
API_HASH = os.environ.get('API_HASH', 'e37e4432298d5a5eb4a6e32c18804283') 
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8813217868:AAFplgrX7Kie_rzursBp1u689UJW5GyhsJ0')

IMG_URL = "https://cdn.pixabay.com/photo/2024/09/22/23/01/ai-generated-9067131_640.jpg" 
ITEMS_PER_PAGE = 8 
USER_SESSIONS = {}

app = Client("FontStylerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    welcome_text = (
        "Hello! Welcome to the Font Styler Bot.\n\n"
        "This bot converts your normal text into clean, premium English font styles.\n\n"
        "How to use:\n"
        "Type /f Your Text Here\n\n"
        "Click the buttons below for more info."
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("About", callback_data="about_bot"),
            InlineKeyboardButton("Help", callback_data="help_bot")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close_menu")
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
        return await message.reply_text("Format Error!\nUse correct format:\n/f Your Text")
        
    user_text = message.text.split(None, 1)[1]
    user_id = message.from_user.id
    USER_SESSIONS[user_id] = user_text
    
    await show_fonts_page(message, user_text, page=0)

@app.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    if data == "about_bot":
        text = "About This Bot:\n\n• Language: Python 3\n• Library: Pyrogram\n• Fonts: English Only Styles\n\nBuilt for clean text styling."
        await query.answer()
        await query.message.edit_caption(caption=text, reply_markup=get_back_keyboard("start_menu"))
        
    elif data == "help_bot":
        text = "Help Menu:\n\n1. Type /f followed by your text.\nExample: /f Hello World\n2. The bot displays styled font buttons.\n3. Tap any style button to instantly copy it."
        await query.answer()
        await query.message.edit_caption(caption=text, reply_markup=get_back_keyboard("start_menu"))
        
    elif data == "start_menu":
        welcome_text = "Hello! Welcome to the Font Styler Bot.\n\nType /f Your Text Here"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("About", callback_data="about_bot"), InlineKeyboardButton("Help", callback_data="help_bot")],
            [InlineKeyboardButton("Close", callback_data="close_menu")]
        ])
        await query.answer()
        await query.message.edit_caption(caption=welcome_text, reply_markup=keyboard)
        
    elif data == "close_menu":
        await query.answer()
        await query.message.delete()
        
    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        if user_id not in USER_SESSIONS:
            return await query.answer("Session expired. Please send /f text again.", show_alert=True)
            
        text = USER_SESSIONS[user_id]
        await query.answer()
        await edit_fonts_page(query.message, text, page)
        
    elif data.startswith("copy_"):
        style_idx = int(data.split("_")[1])
        if user_id not in USER_SESSIONS:
            return await query.answer("Session expired. Please send /f text again.", show_alert=True)
            
        original_text = USER_SESSIONS[user_id]
        styled_text = apply_style(original_text, style_idx)
        
        copy_msg = f"Style Applied! Tap text below to copy:\n\n`{styled_text}`"
        
        await query.answer("Style Generated!", show_alert=False)
        await client.send_message(user_id, copy_msg)

def get_back_keyboard(callback_data: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=callback_data)],
        [InlineKeyboardButton("Close", callback_data="close_menu")]
    ])

async def show_fonts_page(message: Message, text: str, page: int):
    keyboard = build_fonts_keyboard(text, page)
    await message.reply_text(
        f"Choose a Font Style:\n\nYour Text: `{text}`\nPage: {page + 1}",
        reply_markup=keyboard
    )

async def edit_fonts_page(message: Message, text: str, page: int):
    keyboard = build_fonts_keyboard(text, page)
    await message.edit_text(
        f"Choose a Font Style:\n\nYour Text: `{text}`\nPage: {page + 1}",
        reply_markup=keyboard
    )

def build_fonts_keyboard(text: str, page: int):
    total_styles = get_total_styles()
    total_pages = (total_styles + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_styles)
    
    buttons = []
    
    for i in range(start_idx, end_idx):
        preview_text = apply_style(text[:12] + ".." if len(text) > 12 else text, i)
        buttons.append([InlineKeyboardButton(preview_text, callback_data=f"copy_{i}")])
        
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("Pre", callback_data=f"page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next", callback_data=f"page_{page+1}"))
        
    buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton("Close Menu", callback_data="close_menu")])
    
    return InlineKeyboardMarkup(buttons)

if __name__ == "__main__":
    ascii_art = r"""
  ____  _       _                            
 / ___|| |_   _| | ___ _ __   /\/\   ___   _ 
 \___ \| | | | | |/ _ \ '__| /    \ / _ \ (_)
  ___) | | |_| | |  __/ |   / /\/\ \  __/  _ 
 |____/|_|\__, |_|\___|_|   \/    \/\___| (_)
          |___/                              
    """
    print(ascii_art)
    print("Web server started! Bot is live and connecting to Telegram...")
    app.run()
