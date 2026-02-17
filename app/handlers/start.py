"""Start command handler."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.main import get_main_menu_keyboard
from app.database import db

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    user = message.from_user
    chat = message.chat
    
    # Check if it's a group chat
    if chat.type in ["group", "supergroup"]:
        # Bot was added to a group
        bot_info = message.bot
        
        # Try to get chat administrators to find the owner
        try:
            admins = await bot_info.get_chat_administrators(chat.id)
            owner_id = str(user.id)
            
            # Find the actual owner (creator)
            for admin in admins:
                if admin.status == "creator":
                    owner_id = str(admin.user.id)
                    break
            
            # Register the group
            db.add_group(
                group_id=chat.id,
                group_name=chat.title or "Unknown Group",
                owner_id=int(owner_id)
            )
            
            welcome_text = f"""👋 大家好！我是群聊摘要助手！

我可以帮助你们：
• 📝 自动记录群聊消息
• 📊 生成群聊摘要

使用方法：
• /summary - 生成群聊摘要
• /help - 查看帮助

只有群主可以使用管理功能，快去试试吧！"""
            
        except Exception as e:
            welcome_text = f"""👋 大家好！我是群聊摘要助手！

注意：需要群主权限才能正常使用所有功能。

使用方法：
• /summary - 生成群聊摘要
• /help - 查看帮助"""
        
        await message.answer(welcome_text)
    
    else:
        # Direct message to bot
        welcome_text = f"""👋 欢迎 {user.first_name}!

我是群聊摘要助手，可以帮助你：
• 📝 自动记录群聊消息
• 📊 使用AI生成群聊摘要

将我添加到你的Telegram群聊即可开始使用！

使用 /help 查看所有命令。"""
        
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
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
    
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())
