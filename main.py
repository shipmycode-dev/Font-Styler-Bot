# main.py
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from style import apply_style, get_total_styles

# ================= ENVIRONMENT VARIABLES =================
# User github se dale ya deployment settings se, dono support karega.
API_ID = int(os.environ.get('API_ID', '1234567')) # Apni default API ID replace kar dena if needed
API_HASH = os.environ.get('API_HASH', 'YOUR_API_HASH') 
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')

# ================= CONSTANTS & MEDIA =================
IMG_URL = "https://cdn.pixabay.com/photo/2024/09/22/23/01/ai-generated-9067131_640.jpg" # Apna welcome image URL daal de yaha
ITEMS_PER_PAGE = 10 

# In-memory session data save karne ke liye (Taki heavy text limits avoid ho sake)
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
    
    # Image + Text
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
    
    # Store text in session memory
    USER_SESSIONS[user_id] = user_text
    
    # Send First Page
    await show_fonts_page(message, user_text, page=0)

# ================= CALLBACK QUERIES (BUTTON ACTIONS) =================

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
        
        # Advance Trick: Sending monospace format text so clicking on it copies it directly
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
    
    # Har button me uska apna font style dikhega as preview
    for i in range(start_idx, end_idx):
        preview_text = apply_style(text[:15] + ".." if len(text) > 15 else text, i)
        buttons.append([InlineKeyboardButton(preview_text, callback_data=f"copy_{i}")])
        
    # Navigation Buttons (Pre - Back - Next)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Pre", callback_data=f"page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
        
    buttons.append(nav_buttons)
    return InlineKeyboardMarkup(buttons)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
