"""MiniMax API service for text generation."""
import json
from typing import Optional

import aiohttp

from app.config import config


class MiniMaxService:
    """MiniMax API wrapper."""
    
    def __init__(self):
        self.api_key = config.MINIMAX_API_KEY
        self.group_id = config.MINIMAX_GROUP_ID
        self.base_url = config.MINIMAX_BASE_URL
    
    async def generate_summary(
        self,
        messages: list[dict],
        language: str = "zh-CN",
        length: str = "medium"
    ) -> Optional[str]:
        """
        Generate a summary of messages using MiniMax API.
        
        Args:
            messages: List of message dicts with user_name, text, timestamp
            language: Output language (zh-CN, en, etc.)
            length: Summary length (short, medium, long)
        
        Returns:
            Generated summary text or None on error
        """
        # Build prompt based on length
        length_prompt = {
            "short": "简洁地总结，最多100字",
            "medium": "中等长度总结，约200字",
            "long": "详细总结，约400字"
        }.get(length, "中等长度总结，约200字")
        
        # Format messages for the prompt
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(f"{msg.get('user_name', '用户')}: {msg.get('text', '')}")
        
        messages_text = "\n".join(formatted_messages)
        
        # Build the prompt
        system_prompt = f"""你是一个群聊摘要助手。请根据以下群聊消息生成摘要。
要求：
1. 使用{language}语言
2. {length_prompt}
3. 突出讨论重点和关键结论
4. 如果有分歧意见也需要指出
5. 保持客观简洁"""

        user_prompt = f"""群聊消息记录：
{messages_text}

请生成摘要："""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/text/chatcompletion_v2",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "abab6.5s-chat",
                        "group_id": self.group_id,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2048
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        print(f"MiniMax API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"MiniMax API exception: {e}")
            return None
    
    async def generate_summary_simple(
        self,
        messages_text: str,
        language: str = "zh-CN"
    ) -> Optional[str]:
        """
        Generate a simple summary from raw text.
        
        Args:
            messages_text: Raw messages as text
            language: Output language
        
        Returns:
            Generated summary or None on error
        """
        system_prompt = f"""你是一个群聊摘要助手。请简洁地总结群聊内容，使用{language}语言。"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/text/chatcompletion_v2",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "abab6.5s-chat",
                        "group_id": self.group_id,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"请总结以下群聊内容：\n{messages_text}"}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1024
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        print(f"MiniMax API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"MiniMax API exception: {e}")
            return None


# Global service instance
minimax_service = MiniMaxService()
