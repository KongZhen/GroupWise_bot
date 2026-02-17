"""Settings command handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.database import db
from app.keyboards.main import (
    get_settings_keyboard,
    get_summary_length_keyboard,
    get_language_keyboard
)

router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Handle /settings command."""
    chat = message.chat
    user = message.from_user
    
    # Check if in group
    if chat.type not in ["group", "supergroup"]:
        await message.answer("❌ 此命令只能在群聊中使用")
        return
    
    # Check if user is owner
    if not db.is_group_owner(chat.id, user.id):
        await message.answer("⚠️ 只有群主可以使用此命令")
        return
    
    # Get current settings
    group = db.get_group(chat.id)
    
    if not group:
        await message.answer("❌ 群组未注册，请先发送 /start")
        return
    
    settings_text = f"""⚙️ 群设置

群组：{group.group_name}
摘要长度：{group.summary_length}
语言：{group.language}

选择下方按钮进行设置："""
    
    await message.answer(
        settings_text,
        reply_markup=get_settings_keyboard({
            "summary_length": group.summary_length,
            "language": group.language
        })
    )


# Callback query handlers
@router.callback_query(F.data == "action_settings")
async def callback_settings(callback: CallbackQuery):
    """Handle settings button click."""
    chat = callback.message.chat
    user = callback.from_user
    
    if not db.is_group_owner(chat.id, user.id):
        await callback.answer("只有群主可以设置", show_alert=True)
        return
    
    group = db.get_group(chat.id)
    
    if not group:
        await callback.answer("群组未注册", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"""⚙️ 群设置

群组：{group.group_name}
摘要长度：{group.summary_length}
语言：{group.language}

选择下方按钮进行设置：""",
        reply_markup=get_settings_keyboard({
            "summary_length": group.summary_length,
            "language": group.language
        })
    )
    await callback.answer()


@router.callback_query(F.data == "settings_length")
async def callback_settings_length(callback: CallbackQuery):
    """Handle length setting."""
    chat = callback.message.chat
    user = callback.from_user
    
    if not db.is_group_owner(chat.id, user.id):
        await callback.answer("只有群主可以设置", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📏 选择摘要长度：",
        reply_markup=get_summary_length_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings_language")
async def callback_settings_language(callback: CallbackQuery):
    """Handle language setting."""
    chat = callback.message.chat
    user = callback.from_user
    
    if not db.is_group_owner(chat.id, user.id):
        await callback.answer("只有群主可以设置", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🌐 选择语言：",
        reply_markup=get_language_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("length_"))
async def callback_set_length(callback: CallbackQuery):
    """Set summary length."""
    chat = callback.message.chat
    user = callback.from_user
    
    if not db.is_group_owner(chat.id, user.id):
        await callback.answer("只有群主可以设置", show_alert=True)
        return
    
    length = callback.data.replace("length_", "")
    
    db.update_group_settings(chat.id, summary_length=length)
    
    group = db.get_group(chat.id)
    
    await callback.message.edit_text(
        f"""⚙️ 群设置

群组：{group.group_name}
摘要长度：{group.summary_length}
语言：{group.language}

选择下方按钮进行设置：""",
        reply_markup=get_settings_keyboard({
            "summary_length": group.summary_length,
            "language": group.language
        })
    )
    await callback.answer(f"✅ 摘要长度已设置为 {length}")


@router.callback_query(F.data.startswith("lang_"))
async def callback_set_language(callback: CallbackQuery):
    """Set language."""
    chat = callback.message.chat
    user = callback.from_user
    
    if not db.is_group_owner(chat.id, user.id):
        await callback.answer("只有群主可以设置", show_alert=True)
        return
    
    language = callback.data.replace("lang_", "")
    
    db.update_group_settings(chat.id, language=language)
    
    group = db.get_group(chat.id)
    
    await callback.message.edit_text(
        f"""⚙️ 群设置

群组：{group.group_name}
摘要长度：{group.summary_length}
语言：{group.language}

选择下方按钮进行设置：""",
        reply_markup=get_settings_keyboard({
            "summary_length": group.summary_length,
            "language": group.language
        })
    )
    await callback.answer(f"✅ 语言已设置为 {language}")
