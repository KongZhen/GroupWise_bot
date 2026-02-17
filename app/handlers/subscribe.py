"""Subscribe command handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.keyboards.main import get_subscribe_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """Handle /subscribe command."""
    chat = message.chat
    user = message.from_user
    
    # Can be used in group or DM
    
    subscribe_text = """💎 订阅服务

【免费版功能】
• 记录群聊消息
• 生成摘要（需要10条以上消息）

【付费版功能】
• 无限制生成摘要
• 更长的摘要内容
• 优先处理

【价格】
• 月付：¥9.9/月
• 年付：¥99/年

点击下方按钮升级为付费用户！"""
    
    await message.answer(subscribe_text, reply_markup=get_subscribe_keyboard())


@router.callback_query(F.data == "action_subscribe")
async def callback_subscribe(callback: CallbackQuery):
    """Handle subscribe button."""
    await callback.message.edit_text(
        """💎 订阅服务

【免费版功能】
• 记录群聊消息
• 生成摘要（需要10条以上消息）

【付费版功能】
• 无限制生成摘要
• 更长的摘要内容
• 优先处理

【价格】
• 月付：¥9.9/月
• 年付：¥99/年

点击下方按钮升级为付费用户！""",
        reply_markup=get_subscribe_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "subscribe_upgrade")
async def callback_subscribe_upgrade(callback: CallbackQuery):
    """Handle upgrade button."""
    # In production, this would integrate with payment system
    await callback.answer(
        "💳 支付功能开发中...\n\n"
        "请联系群主手动添加付费用户！",
        show_alert=True
    )


@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    """Handle back to main menu."""
    user = callback.from_user
    
    await callback.message.edit_text(
        f"👋 欢迎 {user.first_name}!\n\n"
        "请选择功能：",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "action_help")
async def callback_help(callback: CallbackQuery):
    """Handle help button."""
    help_text = """📖 帮助信息

【可用命令】

🤖 通用命令：
/start - 欢迎消息
/help - 查看帮助
/subscribe - 订阅页面

📝 摘要命令：
/summary - 生成群聊摘要

⚙️ 群主命令：
/settings - 群设置
/addpaid <用户ID> - 添加付费用户
/paidlist - 付费用户列表

【使用说明】

1. 将Bot添加到群聊
2. Bot会自动记录消息
3. 使用 /summary 生成摘要

【权限说明】

• 所有人：生成摘要、查看帮助
• 群主：管理设置、添加付费用户

如有疑问，请联系管理员。"""
    
    await callback.message.edit_text(help_text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "action_summary")
async def callback_summary_button(callback: CallbackQuery):
    """Handle summary button - tell user to use command in group."""
    await callback.answer(
        "请在群聊中使用 /summary 命令生成摘要",
        show_alert=True
    )
