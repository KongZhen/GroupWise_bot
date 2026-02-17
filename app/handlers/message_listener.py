"""Message listener - stores messages from group chats."""
from aiogram import Router, F
from aiogram.types import Message

from app.database import db
from app.services.message_store import message_store

router = Router()


@router.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_message(message: Message):
    """Handle messages in group chats."""
    # Ignore commands
    if message.text and message.text.startswith("/"):
        return
    
    # Ignore bot messages
    if message.from_user.is_bot:
        return
    
    # Get user info
    user = message.from_user
    user_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or f"User_{user.id}"
    
    # Get message text
    text = message.text or ""
    
    # Also include captions from media
    if message.caption:
        text = f"{text} {message.caption}".strip()
    
    if not text:
        return
    
    # Store the message
    await message_store.store_message(
        group_id=message.chat.id,
        user_id=user.id,
        user_name=user_name,
        text=text
    )
