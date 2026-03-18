import asyncio
import os
import yt_dlp
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiohttp import web

# ================== BOSH QISMI (SIZNING KALITLARINGIZ) ==================
BOT_TOKEN = "8517967499:AAGoXzbc_4FXOGdFJ7yx96sxFkDs94wmOHo"
GEMINI_API_KEY = "AIzaSyAb2I7hZvVvsQJxbrI2gYyb9LIv3bRh0XQ"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== SERVERNI UYG'OQ TUTISH (24/7) ==================
async def handle_ping(request):
    return web.Response(text="Bot 24/7 ishlab turibdi! Hech qanday cheklov yo'q.")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

# ================== PROFESSIONAL YUKLAB OLISH ==================
async def smart_downloader(url: str, message: types.Message, is_audio=False):
    status = await message.answer("🔄 <i>Kuting, kontent olinmoqda...</i>", parse_mode="HTML")
    
    ydl_opts = {
        'format': 'bestaudio/best' if is_audio else 'best[filesize<50M]/best',
        'outtmpl': 'downloaded_%(id)s.%(ext)s',
        'quiet': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    if is_audio:
        ydl_opts['postprocessors'] =[{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]

    if not url.startswith("http"):
        url = f"ytsearch:{url}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return await status.edit_text("❌ Bu kontentni sayt qulflab qo'ygan.")
            
            info = info['entries'][0] if 'entries' in info else info
            filename = f"downloaded_{info['id']}.mp3" if is_audio else f"downloaded_{info['id']}.{info['ext']}"
            
            if not os.path.exists(filename):
                return await status.edit_text("❌ Yuklab olishda xatolik. Video yopiq bo'lishi mumkin.")

            file_send = FSInputFile(filename)
            await status.edit_text("🚀 <i>Telegramga yuborilmoqda...</i>", parse_mode="HTML")
            
            if is_audio:
                await message.answer_audio(file_send, title=info.get('title', 'Musiqa'))
            else:
                await message.answer_video(file_send, caption=info.get('title', 'Video'))
                
            os.remove(filename)
            await status.delete()
            
    except Exception as e:
        await status.edit_text("⚠️ <b>Xatolik:</b> Telegram hajmi maksimal 50MB gacha ruxsat beradi yoki sayt himoyalangan.", parse_mode="HTML")

# ================== XABARLAR VA GEMINI AI ==================
@dp.message(F.text)
async def main_handler(message: types.Message):
    text = message.text
    
    if text == "/start":
        await message.answer("👋 Salom! Men Universal Botman.\n🔗 Menga YouTube, Instagram, TikTok ssilkasini tashlang.\n🎵 'musiqa [nomi]' deb yozing - qo'shiq tashlayman.\n🧠 Yoki istalgan savolingizni bering - javob beraman!")
        return

    # Havola kelsa -> Video
    if "http://" in text or "https://" in text:
        await smart_downloader(text, message, is_audio=False)
    
    # Musiqa so'ralsa -> Mp3
    elif text.lower().startswith("musiqa ") or text.lower().startswith("mp3 "):
        song = text.lower().replace("musiqa ", "").replace("mp3 ", "")
        await smart_downloader(song, message, is_audio=True)
    
    # Boshqa savollar -> Gemini S.I.
    else:
        status = await message.answer("💬 <i>O'ylayapman...</i>", parse_mode="HTML")
        try:
            response = model.generate_content(text)
            await status.edit_text(response.text)
        except Exception:
            await status.edit_text("❌ Sun'iy intellektga ulanishda xato. Keyinroq urinib ko'ring.")

# ================== ISHGA TUSHIRISH ==================
async def main():
    await start_web_server()
    print("✅ UNIVERSAL BOT ISHGA TUSHDI! 24/7 ISHLAMOQDA...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
