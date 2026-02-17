"""Paid users management handler."""
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.database import db

router = Router()


@router.message(Command("addpaid"))
async def cmd_add_paid(message: Message):
    """Handle /addpaid command."""
    chat = message.chat
    user = message.from_user
    
    # Check if in group
    if chat.type not in ["group", "supergroup"]:
        await message.answer("❌ 此命令只能在群聊中使用")
        return
    
    # Check if user is owner
    if not db.is_group_owner(chat.id, user.id):
        await message.answer("⚠️ 只有群主可以添加付费用户")
        return
    
    # Parse command arguments
    args = message.text.split()
    
    if len(args) < 2:
        await message.answer(
            "📝 用法：/addpaid <用户ID> [天数]\n\n"
            "示例：\n"
            "• /addpaid 123456789 30 (添加30天)\n"
            "• /addpaid 123456789 (默认30天)"
        )
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ 用户ID必须是数字")
        return
    
    # Get days (default 30)
    days = 30
    if len(args) >= 3:
        try:
            days = int(args[2])
        except ValueError:
            await message.answer("❌ 天数必须是数字")
            return
    
    # Calculate expire date
    expire_date = (datetime.now() + timedelta(days=days)).isoformat()
    
    # Get username
    user_name = f"User_{target_user_id}"
    if len(args) >= 4:
        user_name = " ".join(args[3:])
    else:
        # Try to get from Telegram
        try:
            chat_member = await message.bot.get_chat_member(chat.id, target_user_id)
            if chat_member and chat_member.user:
                user_name = chat_member.user.first_name or user_name
                if chat_member.user.last_name:
                    user_name += f" {chat_member.user.last_name}"
        except Exception:
            pass
    
    # Add paid user
    success = db.add_paid_user(target_user_id, user_name, chat.id, expire_date)
    
    if success:
        expire_str = datetime.fromisoformat(expire_date).strftime("%Y-%m-%d")
        await message.answer(
            f"✅ 已添加付费用户\n\n"
            f"👤 用户：{user_name} (ID: {target_user_id})\n"
            f"📅 过期时间：{expire_str}\n"
            f"⏱️ 时长：{days}天"
        )
    else:
        await message.answer("❌ 添加付费用户失败")


@router.message(Command("paidlist"))
async def cmd_paid_list(message: Message):
    """Handle /paidlist command."""
    chat = message.chat
    user = message.from_user
    
    # Check if in group
    if chat.type not in ["group", "supergroup"]:
        await message.answer("❌ 此命令只能在群聊中使用")
        return
    
    # Check if user is owner
    if not db.is_group_owner(chat.id, user.id):
        await message.answer("⚠️ 只有群主可以查看付费用户列表")
        return
    
    # Get paid users
    paid_users = db.get_paid_users(chat.id)
    
    if not paid_users:
        await message.answer("📭 暂无付费用户")
        return
    
    # Build list
    now = datetime.now()
    lines = ["💎 付费用户列表\n"]
    
    for i, pu in enumerate(paid_users, 1):
        expire_date = datetime.fromisoformat(pu.expire_date)
        is_expired = expire_date < now
        status = "🔴 已过期" if is_expired else "🟢 有效"
        
        expire_str = expire_date.strftime("%Y-%m-%d")
        
        lines.append(
            f"{i}. {pu.user_name} ({pu.user_id})\n"
            f"   📅 过期：{expire_str} {status}"
        )
    
    lines.append(f"\n━━━━━━━━━━━━━━━━━━\n共 {len(paid_users)} 位付费用户")
    
    await message.answer("\n".join(lines))


# Callback for removing paid user
@router.callback_query(F.data.startswith("remove_paid_"))
async def callback_remove_paid(callback: CallbackQuery):
    """Handle removing paid user."""
    chat = callback.message.chat
    user = callback.from_user
    
    if not db.is_group_owner(chat.id, user.id):
        await callback.answer("只有群主可以操作", show_alert=True)
        return
    
    # Parse user_id from callback data
    try:
        user_id = int(callback.data.replace("remove_paid_", ""))
    except ValueError:
        await callback.answer("无效的用户ID", show_alert=True)
        return
    
    success = db.remove_paid_user(user_id, chat.id)
    
    if success:
        await callback.answer("✅ 已移除付费用户", show_alert=True)
        # Refresh the list
        paid_users = db.get_paid_users(chat.id)
        
        if not paid_users:
            await callback.message.edit_text("📭 暂无付费用户")
        else:
            now = datetime.now()
            lines = ["💎 付费用户列表\n"]
            
            for i, pu in enumerate(paid_users, 1):
                expire_date = datetime.fromisoformat(pu.expire_date)
                is_expired = expire_date < now
                status = "🔴 已过期" if is_expired else "🟢 有效"
                expire_str = expire_date.strftime("%Y-%m-%d")
                
                lines.append(
                    f"{i}. {pu.user_name} ({pu.user_id})\n"
                    f"   📅 过期：{expire_str} {status}"
                )
            
            await callback.message.edit_text("\n".join(lines))
    else:
        await callback.answer("❌ 移除失败", show_alert=True)
