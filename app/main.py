"""Bot main entry point."""
import asyncio
import logging
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: web.Application):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting bot...")
    await set_webhook()
    
    yield
    
    # Shutdown
    logger.info("Shutting down bot...")
    await bot.session.close()


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
app = web.Application(lifespan=lifespan)
app.router.add_post("/webhook", handle_webhook)


async def main_polling():
    """Run bot in polling mode (for local development)."""
    await delete_webhook()
    
    logger.info("Starting bot in polling mode...")
    
    await dp.start_polling(bot)


async def main_webhook():
    """Run bot in webhook mode (for Railway)."""
    logger.info("Starting bot in webhook mode...")
    
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", "8080"))
    
    # Create runner
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Start HTTP server
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logger.info(f"HTTP server started on port {port}")
    
    # Keep the server running
    await asyncio.Event().wait()


if __name__ == "__main__":
    import os
    
    # Check if running in webhook mode
    if os.getenv("WEBHOOK_URL"):
        asyncio.run(main_webhook())
    else:
        asyncio.run(main_polling())
