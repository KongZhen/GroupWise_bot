"""Bot main entry point."""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from aiohttp import web

from app.config import config
from app.handlers import start, summary, settings, paid, subscribe
from app.handlers.message_listener import router as message_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Initialize bot and dispatcher
bot = Bot(
    token=config.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Register routers
dp.include_router(start.router)
dp.include_router(summary.router)
dp.include_router(settings.router)
dp.include_router(paid.router)
dp.include_router(subscribe.router)
dp.include_router(message_router)


async def set_webhook():
    """Set webhook for Railway deployment."""
    if config.WEBHOOK_URL:
        webhook_secret = config.WEBHOOK_SECRET
        await bot.set_webhook(
            f"{config.WEBHOOK_URL}/webhook",
            secret_token=webhook_secret
        )
        logger.info(f"Webhook set to {config.WEBHOOK_URL}/webhook")


async def delete_webhook():
    """Delete webhook (for polling mode)."""
    await bot.delete_webhook()
    logger.info("Webhook deleted")


# Webhook handler for Railway
async def handle_webhook(request: web.Request) -> web.Response:
    """Handle incoming webhook requests."""
    try:
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot=bot, update=update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return web.Response(status=500)


# Create aiohttp application
app = web.Application()

# Startup
async def on_startup(app):
    logger.info("Starting bot...")
    await set_webhook()

# Shutdown  
async def on_shutdown(app):
    logger.info("Shutting down bot...")
    await bot.session.close()

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

app.router.add_post("/webhook", handle_webhook)


async def main_polling():
    """Run bot in polling mode (for local development)."""
    await delete_webhook()
    
    logger.info("Starting bot in polling mode...")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "polling":
        # Local development mode
        asyncio.run(main_polling())
    else:
        # Railway webhook mode
        logger.info("Starting Railway webhook server...")
        web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
