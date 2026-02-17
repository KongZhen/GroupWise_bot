"""Summary command handler."""
import asyncio
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import db
from app.services.minimax import minimax_service
from app.services.message_store import message_store

router = Router()


async def can_generate_summary(user_id: int, chat_id: int, is_owner: bool) -> tuple[bool, str]:
    """
    Check if user can generate summary.
    
    Returns:
        (can_generate, reason)
    """
    group = db.get_group(chat_id)
    
    if not group:
        return False, "群组未注册，请先发送 /start"
    
    # Check if user is owner
    if is_owner:
        return True, ""
    
    # Check if user is paid
    if db.is_paid_user(user_id, chat_id):
        return True, ""
    
    # Check if group is premium
    if group.is_premium:
        return False, "此群为付费群，请联系群主订阅或成为付费用户"
    
    # Free tier - allow with limit
    message_count = message_store.get_message_count(chat_id)
    if message_count < 10:
        return False, f"消息不足，需要至少10条消息才能生成摘要（当前: {message_count}条）"
    
    return True, ""


@router.message(Command("summary"))
async def cmd_summary(message: Message):
    """Handle /summary command."""
    chat = message.chat
    user = message.from_user
    
    # Check if in group
    if chat.type not in ["group", "supergroup"]:
        await message.answer("❌ 此命令只能在群聊中使用")
        return
    
    # Check if user is owner
    is_owner = db.is_group_owner(chat.id, user.id)
    
    # Check permission
    can_generate, reason = await can_generate_summary(user.id, chat.id, is_owner)
    
    if not can_generate:
        await message.answer(f"⚠️ {reason}")
        return
    
    # Get group settings
    group = db.get_group(chat.id)
    
    # Get messages
    messages = message_store.get_messages_for_summary(chat.id)
    
    if not messages:
        await message.answer("📭 暂无消息记录，无法生成摘要")
        return
    
    # Send processing message
    processing_msg = await message.answer("⏳ 正在生成摘要，请稍候...")
    
    # Generate summary
    try:
        summary = await minimax_service.generate_summary(
            messages=messages,
            language=group.language,
            length=group.summary_length
        )
        
        if summary:
            result_text = f"📊 群聊摘要\n\n{summary}\n\n━━━━━━━━━━━━━━━━━━\n💬 基于最近 {len(messages)} 条消息生成"
            await processing_msg.edit_text(result_text)
        else:
            await processing_msg.edit_text("❌ 生成摘要失败，请稍后重试")
            
    except Exception as e:
        print(f"Summary generation error: {e}")
        await processing_msg.edit_text("❌ 生成摘要时出错，请稍后重试")
