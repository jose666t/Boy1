from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import instaloader
import yt_dlp
import requests
import re
import logging
from datetime import datetime

# Configuración
TOKEN = "7798898970:AAE2IApy1BOSayigiN9haGR0TpKTBGaKH6U"  # 🔑 Reemplaza con tu token real
L = instaloader.Instaloader()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# APIs para TikTok (3 alternativas)
TIKTOK_APIS = [
    {"url": "https://api.tikmate.app/api/lookup?url={}", "field": "video.download_url"},
    {"url": "https://tikdown.org/api?url={}", "field": "videoUrl"},
    {"url": "https://www.tikwm.com/api/?url={}", "field": "data.play"}
]

# ==================== INTERFAZ ==================== #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Descargar Video", callback_data="download")],
        [
            InlineKeyboardButton("⚙️ Formatos", callback_data="formats"),
            InlineKeyboardButton("📚 Ayuda", callback_data="help")
        ],
        [InlineKeyboardButton("🔗 Ejemplos", callback_data="examples")]
    ]
    await update.message.reply_text(
        "🎬 *Descargador Universal*\n\n"
        "Envía un enlace de:\n"
        "- TikTok\n"
        "- Instagram (Reels/Posts)\n"
        "- YouTube\n\n"
        "O usa los botones:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ==================== MANEJADOR DE BOTONES ==================== #
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "download":
        await query.edit_message_text("⬇️ Envíame el enlace del video")
    elif query.data == "formats":
        await show_formats(query)
    elif query.data == "help":
        await show_help(query)
    elif query.data == "examples":
        await show_examples(query)

# ==================== FUNCIONES AUXILIARES ==================== #
async def show_formats(query):
    formats = (
        "🎛️ *Formatos Disponibles*\n\n"
        "• TikTok: MP4 HD sin marca\n"
        "• Instagram: Videos/Imágenes máxima calidad\n"
        "• YouTube: 720p/1080p/4K y MP3"
    )
    await query.edit_message_text(formats, parse_mode="Markdown")

async def show_help(query):
    help_text = (
        "📘 *Centro de Ayuda*\n\n"
        "1. Copia el enlace del video\n"
        "2. Péglo en este chat\n"
        "3. Espera a que se procese\n\n"
        "⚠️ *Limitaciones:*\n"
        "- Videos hasta 15 minutos\n"
        "- No contenido privado\n\n"
        "🛠 Soporte: @tu_soporte"
    )
    await query.edit_message_text(help_text, parse_mode="Markdown")

async def show_examples(query):
    examples = (
        "🔗 *Ejemplos válidos*\n\n"
        "TikTok:\n`https://vm.tiktok.com/ZM6ejemplo/`\n\n"
        "Instagram:\n`https://www.instagram.com/reel/Cx4GjzXgRkF/`\n\n"
        "YouTube:\n`https://youtu.be/dQw4w9WgXcQ`"
    )
    await query.edit_message_text(examples, parse_mode="Markdown", disable_web_page_preview=True)

# ==================== DESCARGAS ==================== #
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "tiktok.com" in url or "vm.tiktok.com" in url:
        await download_tiktok(update, url)
    elif "instagram.com" in url:
        await download_instagram(update, url)
    elif "youtube.com" in url or "youtu.be" in url:
        await download_youtube(update, url)
    else:
        await update.message.reply_text("⚠️ Enlace no soportado")

async def download_tiktok(update: Update, url: str):
    loading_msg = await update.message.reply_text("🔍 Buscando en servidores...")
    
    for api in TIKTOK_APIS:
        try:
            response = requests.get(api["url"].format(url), timeout=15)
            data = response.json()
            
            # Extracción dinámica del campo
            video_url = data
            for key in api["field"].split('.'):
                if isinstance(video_url, dict):
                    video_url = video_url.get(key)
                else:
                    raise ValueError("Estructura de API inválida")
            
            if video_url:
                await update.message.reply_video(
                    video_url,
                    caption="⬇️ Video de TikTok descargado",
                    supports_streaming=True,
                    width=720,
                    height=1280
                )
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=loading_msg.message_id)
                return
                
        except Exception as e:
            logging.warning(f"API {api['url']} falló: {str(e)}")
            continue
    
    await update.message.reply_text("❌ Todos los servidores fallaron. Intenta más tarde")
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=loading_msg.message_id)

async def download_instagram(update: Update, url: str):
    try:
        if "/reel/" in url or "/p/" in url:
            shortcode = re.findall(r"(?:reel|p)/([A-Za-z0-9_-]+)", url)[0]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            if post.is_video:
                await update.message.reply_video(
                    post.video_url,
                    caption="⬇️ Reel de Instagram descargado",
                    supports_streaming=True
                )
            else:
                await update.message.reply_photo(
                    post.url,
                    caption="⬇️ Post de Instagram descargado"
                )
        else:
            await update.message.reply_text("ℹ️ Solo soporto Reels y Posts públicos")
            
    except IndexError:
        await update.message.reply_text("❌ Formato de enlace incorrecto")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def download_youtube(update: Update, url: str):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' not in info:
                await update.message.reply_text("❌ No se pudo obtener el video")
                return
                
            await update.message.reply_video(
                info['url'],
                caption="⬇️ Video de YouTube descargado",
                supports_streaming=True,
                width=info.get('width', 1280),
                height=info.get('height', 720)
            )
            
    except yt_dlp.DownloadError as e:
        await update.message.reply_text(f"❌ Error en YouTube: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error inesperado: {str(e)}")

# ==================== CONFIGURACIÓN ==================== #
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot iniciado - Listo para descargar!")
    app.run_polling()

if __name__ == "__main__":
    main()
    
