# Telegram Group AI Summary Bot

## 项目结构
```
bot/
├── app/
│   ├── __init__.py
│   ├── main.py          # 入口文件
│   ├── config.py        # 配置
│   ├── database.py      # SQLite数据库
│   ├── handlers/        # 命令处理器
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── summary.py
│   │   ├── settings.py
│   │   ├── paid.py
│   │   └── subscribe.py
│   ├── services/        # 业务服务
│   │   ├── __init__.py
│   │   ├── minimax.py   # MiniMax API
│   │   └── message_store.py  # 消息存储
│   └── keyboards/       # 键盘布局
│       ├── __init__.py
│       └── main.py
├── requirements.txt
├── Dockerfile
├── railway.json
└── .env.example
```

## 快速开始

### 本地开发
```bash
# 1. 复制环境变量配置
cp .env.example .env

# 2. 编辑 .env 填入配置
nano .env

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行Bot
python -m app.main
```

### Railway部署
```bash
# 使用Railway CLI
railway login
railway init
railway deploy
```

## 命令说明

| 命令 | 描述 | 权限 |
|------|------|------|
| /start | 欢迎消息和菜单 | 所有人 |
| /summary | 生成群聊摘要 | 群主/付费用户 |
| /help | 帮助信息 | 所有人 |
| /settings | 设置选项 | 群主 |
| /addpaid <user_id> | 添加付费用户 | 群主 |
| /paidlist | 付费用户列表 | 群主 |
| /subscribe | 订阅页面 | 所有人 |

## 配置项

| 变量 | 描述 | 必需 |
|------|------|------|
| TELEGRAM_BOT_TOKEN | Telegram Bot Token | 是 |
| MINIMAX_API_KEY | MiniMax API Key | 是 |
| MINIMAX_GROUP_ID | MiniMax Group ID | 是 |
| DATABASE_URL | 数据库路径 | 否 |
| ADMIN_USER_ID | 管理员用户ID | 否 |
