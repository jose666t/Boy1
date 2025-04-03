from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import yt_dlp
import instaloader
import requests
import re

# Configuración (REEMPLAZA ESTO CON TU TOKEN REAL)
TOKEN = "7798898970:AAE2IApy1BOSayigiN9haGR0TpKTBGaKH6U"  # ← Inserta tu token entre las comillas
L = instaloader.Instaloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📥 **Descargador de Videos**\n\n"
        "Envía enlaces de:\n"
        "- YouTube\n"
        "- TikTok\n"
        "- Instagram\n"
        "y los descargaré para ti."
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    chat_id = update.effective_chat.id

    try:
        if "tiktok.com" in url:
            # Descarga de TikTok
            api_url = f"https://tikdown.org/api?url={url}"
            response = requests.get(api_url).json()
            video_url = response.get("videoUrl")
            if video_url:
                await context.bot.send_video(chat_id=chat_id, video=video_url)
        
        elif "instagram.com" in url:
            # Descarga de Instagram
            shortcode = re.findall(r"(?:reel|p)/([A-Za-z0-9_-]+)", url)[0]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            if post.is_video:
                await context.bot.send_video(chat_id=chat_id, video=post.video_url)
        
        elif "youtube.com" in url or "youtu.be" in url:
            # Descarga de YouTube
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                await context.bot.send_video(chat_id=chat_id, video=info['url'])
        
        else:
            await update.message.reply_text("⚠️ Plataforma no soportada")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    
    application.run_polling()

if __name__ == "__main__":
    main()