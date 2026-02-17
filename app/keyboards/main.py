"""Inline keyboards for the bot."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 生成摘要", callback_data="action_summary"),
        InlineKeyboardButton(text="⚙️ 设置", callback_data="action_settings")
    )
    builder.row(
        InlineKeyboardButton(text="💳 订阅", callback_data="action_subscribe"),
        InlineKeyboardButton(text="❓ 帮助", callback_data="action_help")
    )
    
    return builder.as_markup()


def get_settings_keyboard(current_settings: dict = None) -> InlineKeyboardMarkup:
    """Settings keyboard."""
    builder = InlineKeyboardBuilder()
    
    # Summary length
    length = current_settings.get("summary_length", "medium") if current_settings else "medium"
    length_text = {
        "short": "🔴 短",
        "medium": "🟡 中",
        "long": "🟢 长"
    }.get(length, "🟡 中")
    
    builder.row(
        InlineKeyboardButton(
            text=f"📏 摘要长度: {length_text}",
            callback_data="settings_length"
        )
    )
    
    # Language
    lang = current_settings.get("language", "zh-CN") if current_settings else "zh-CN"
    lang_text = "🇨🇳 中文" if lang == "zh-CN" else "🇺🇸 English"
    
    builder.row(
        InlineKeyboardButton(
            text=f"🌐 语言: {lang_text}",
            callback_data="settings_language"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="« 返回", callback_data="back_to_main")
    )
    
    return builder.as_markup()


def get_subscribe_keyboard() -> InlineKeyboardMarkup:
    """Subscribe keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💎 升级为付费用户", callback_data="subscribe_upgrade")
    )
    builder.row(
        InlineKeyboardButton(text="« 返回", callback_data="back_to_main")
    )
    
    return builder.as_markup()


def get_summary_length_keyboard() -> InlineKeyboardMarkup:
    """Summary length selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔴 短 (100字)", callback_data="length_short"),
        InlineKeyboardButton(text="🟡 中 (200字)", callback_data="length_medium"),
        InlineKeyboardButton(text="🟢 长 (400字)", callback_data="length_long")
    )
    builder.row(
        InlineKeyboardButton(text="« 返回", callback_data="action_settings")
    )
    
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh-CN"),
        InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
    )
    builder.row(
        InlineKeyboardButton(text="« 返回", callback_data="action_settings")
    )
    
    return builder.as_markup()


def get_confirm_keyboard(confirm_action: str, cancel_action: str = "back_to_main") -> InlineKeyboardMarkup:
    """Generic confirm/cancel keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ 确认", callback_data=confirm_action),
        InlineKeyboardButton(text="❌ 取消", callback_data=cancel_action)
    )
    
    return builder.as_markup()
