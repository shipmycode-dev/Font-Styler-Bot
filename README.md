# Advance Font Styler Bot

A fast, interactive Telegram Bot that converts text into 50+ premium fonts with pagination and single-tap copy functionality.

## Features
- **Advance Welcome Message** with Images and Inline Buttons (About, Help).
- Commands: `/f {your text}` converts normal text to stylish fonts.
- **Dynamic Previews**: Font preview directly inside the inline keyboard buttons.
- **Next/Pre Pagination**: Easily navigate through 50+ fonts.
- **Tap-to-Copy**: Click the generated font to copy it automatically.
- Fallback & Environmental variables supported (`API_ID`, `API_HASH`, `BOT_TOKEN`).

## Deployment Instructions

### Render / Koyeb / Heroku / Railway
1. Fork this repository.
2. Link your GitHub repository to your host platform.
3. Add the following **Environment Variables** in the platform settings:
   - `API_ID` (Get from my.telegram.org)
   - `API_HASH` (Get from my.telegram.org)
   - `BOT_TOKEN` (Get from @BotFather)
4. The deployment will automatically detect `requirements.txt` and `Procfile`.
5. Run!

### Local Run
```bash
pip install -r requirements.txt
python main.py
