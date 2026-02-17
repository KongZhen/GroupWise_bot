"""Bot main entry point."""
import logging
import sys
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

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


# Webhook path
WEBHOOK_PATH = "/webhook"


async def on_startup(bot: Bot) -> None:
    """Set webhook on startup."""
    if config.WEBHOOK_URL:
        await bot.set_webhook(
            f"{config.WEBHOOK_URL}{WEBHOOK_PATH}",
            secret_token=config.WEBHOOK_SECRET or None
        )
        logger.info(f"Webhook set to {config.WEBHOOK_URL}{WEBHOOK_PATH}")
    else:
        logger.warning("WEBHOOK_URL not set, skipping webhook setup")


# Register startup/shutdown hooks via dispatcher (aiogram 3.x best practice)
dp.startup.register(on_startup)


async def main_polling():
    """Run bot in polling mode (for local development)."""
    await bot.delete_webhook()
    logger.info("Webhook deleted")
    
    logger.info("Starting bot in polling mode...")
    
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point for Railway webhook mode."""
    # Create aiohttp application
    app = web.Application()
    
    # Create webhook request handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.WEBHOOK_SECRET or None,
    )
    
    # Register webhook handler
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)
    
    # Start webserver
    web.run_app(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    if len(sys.argv) > 1 and sys.argv[1] == "polling":
        # Local development mode
        import asyncio
        asyncio.run(main_polling())
    else:
        # Railway webhook mode
        logger.info("Starting Railway webhook server...")
        main()