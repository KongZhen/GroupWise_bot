"""Message store service."""
from app.database import db


class MessageStore:
    """Message storage and retrieval."""
    
    # Maximum messages to store per group
    MAX_MESSAGES = 1000
    
    # Messages to keep for summary
    SUMMARY_MESSAGE_LIMIT = 200
    
    @staticmethod
    async def store_message(group_id: int, user_id: int, user_name: str, text: str):
        """Store a message from the group."""
        if not text or not text.strip():
            return
        
        # Store in database
        db.add_message(group_id, user_id, user_name, text)
        
        # Cleanup old messages if needed
        count = db.get_message_count(group_id)
        if count > MessageStore.MAX_MESSAGES:
            # Keep only the most recent messages
            db.trim_messages(group_id, MessageStore.MAX_MESSAGES)
    
    @staticmethod
    def get_messages_for_summary(group_id: int) -> list[dict]:
        """Get messages for summary generation."""
        return db.get_recent_messages(group_id, MessageStore.SUMMARY_MESSAGE_LIMIT)
    
    @staticmethod
    def get_message_count(group_id: int) -> int:
        """Get total message count."""
        return db.get_message_count(group_id)


message_store = MessageStore()
