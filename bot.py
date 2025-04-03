from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
import yt_dlp
import instaloader
import requests
import re
import logging
from datetime import datetime

#  ======== CONFIGURACIÓN PREMIUM ======== #
TOKEN = "7798898970:AAE2IApy1BOSayigiN9haGR0TpKTBGaKH6U"
ADMIN_ID =  7659958667 # Reemplaza con tu ID
LOG_FILE = "premium_bot.log"

# Configuración de logging
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Módulo de fuentes especiales
class FontStyles:
    @staticmethod
    def bold(text):
        return f"*{text}*"
    
    @staticmethod
    def italic(text):
        return f"_{text}_"
    
    @staticmethod
    def bold_italic(text):
        return f"*_{text}_*"
    
    @staticmethod
    def code(text):
        return f"`{text}`"

#  ======== FUNCIONES PREMIUM ======== #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_msg = FontStyles.bold_italic("🎉 ¡Bienvenido al Descargador Premium!") + "\n\n"
    welcome_msg += FontStyles.italic("Envía un enlace de:") + "\n"
    welcome_msg += "• YouTube\n• TikTok\n• Instagram"
    
    keyboard = [
        [InlineKeyboardButton("📚 Ayuda", callback_data="help"),
         InlineKeyboardButton("⭐ Premium", callback_data="premium")]
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user = update.effective_user
    
    try:
        loading_msg = await update.message.reply_text(
            FontStyles.italic("🔍 Procesando tu enlace..."),
            parse_mode="MarkdownV2"
        )
        
        if "tiktok.com" in url:
            await handle_tiktok(update, context, url)
        elif "instagram.com" in url:
            await handle_instagram(update, context, url)
        elif "youtube.com" in url or "youtu.be" in url:
            await handle_youtube(update, context, url)
        else:
            await update.message.reply_text(
                FontStyles.bold("⚠ Plataforma no soportada"),
                parse_mode="MarkdownV2"
            )
            
    except Exception as e:
        logger.error(f"Error para @{user.username}: {str(e)}")
        await update.message.reply_text(
            FontStyles.bold("❌ Error: ") + f"`{str(e)}`",
            parse_mode="MarkdownV2"
        )
    finally:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=loading_msg.message_id
        )

#  ======== FUNCIONES DE DESCARGA MEJORADAS ======== #
async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    keyboard = [
        [InlineKeyboardButton("🎥 Video", callback_data=f"yt_video|{url}"),
         InlineKeyboardButton("🎵 Audio", callback_data=f"yt_audio|{url}")]
    ]
    
    await update.message.reply_text(
        FontStyles.bold("🎬 Selecciona el formato:"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    # Implementación profesional con manejo de errores
    pass

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    # Implementación profesional con manejo de errores
    pass

#  ======== MAIN ======== #
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    
    # Iniciar bot
    app.run_polling()

if __name__ == "__main__":
    print(FontStyles.bold("Iniciando bot premium..."))
    main()
