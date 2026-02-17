"""SQLite database management."""
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional

from app.config import config


@dataclass
class GroupSettings:
    """Group settings."""
    group_id: int
    group_name: str
    owner_id: int
    is_premium: bool = False
    summary_length: str = "medium"  # short, medium, long
    language: str = "zh-CN"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class PaidUser:
    """Paid user record."""
    user_id: int
    user_name: str
    group_id: int
    expire_date: str
    created_at: str = ""


class Database:
    """SQLite database wrapper."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_URL
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @contextmanager
    def _cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager for cursor."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables."""
        with self._cursor() as cursor:
            # Groups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    group_name TEXT NOT NULL,
                    owner_id INTEGER NOT NULL,
                    is_premium INTEGER DEFAULT 0,
                    summary_length TEXT DEFAULT 'medium',
                    language TEXT DEFAULT 'zh-CN',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Paid users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paid_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT,
                    group_id INTEGER NOT NULL,
                    expire_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, group_id)
                )
            """)
            
            # Messages table (for summary)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    user_name TEXT,
                    text TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_group_time 
                ON messages(group_id, timestamp)
            """)
    
    # ========== Group Operations ==========
    
    def add_group(self, group_id: int, group_name: str, owner_id: int) -> GroupSettings:
        """Add or update a group."""
        now = datetime.now().isoformat()
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT INTO groups (group_id, group_name, owner_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(group_id) DO UPDATE SET
                    group_name = excluded.group_name,
                    owner_id = excluded.owner_id,
                    updated_at = excluded.updated_at
            """, (group_id, group_name, owner_id, now, now))
        
        return self.get_group(group_id)
    
    def get_group(self, group_id: int) -> Optional[GroupSettings]:
        """Get group settings."""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
            row = cursor.fetchone()
            
            if row:
                return GroupSettings(
                    group_id=row["group_id"],
                    group_name=row["group_name"],
                    owner_id=row["owner_id"],
                    is_premium=bool(row["is_premium"]),
                    summary_length=row["summary_length"],
                    language=row["language"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
        return None
    
    def update_group_settings(self, group_id: int, **kwargs) -> bool:
        """Update group settings."""
        allowed_fields = {"is_premium", "summary_length", "language"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates["updated_at"] = datetime.now().isoformat()
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [group_id]
        
        with self._cursor() as cursor:
            cursor.execute(
                f"UPDATE groups SET {set_clause} WHERE group_id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def is_group_owner(self, group_id: int, user_id: int) -> bool:
        """Check if user is group owner."""
        group = self.get_group(group_id)
        return group and group.owner_id == user_id
    
    # ========== Paid Users Operations ==========
    
    def add_paid_user(self, user_id: int, user_name: str, group_id: int, expire_date: str) -> bool:
        """Add a paid user."""
        now = datetime.now().isoformat()
        with self._cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO paid_users (user_id, user_name, group_id, expire_date, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, user_name, group_id, expire_date, now))
                return True
            except sqlite3.IntegrityError:
                # Update existing
                cursor.execute("""
                    UPDATE paid_users 
                    SET user_name = ?, expire_date = ?
                    WHERE user_id = ? AND group_id = ?
                """, (user_name, expire_date, user_id, group_id))
                return True
        return False
    
    def get_paid_users(self, group_id: int) -> list[PaidUser]:
        """Get all paid users for a group."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT * FROM paid_users 
                WHERE group_id = ?
                ORDER BY expire_date DESC
            """, (group_id,))
            
            return [
                PaidUser(
                    user_id=row["user_id"],
                    user_name=row["user_name"],
                    group_id=row["group_id"],
                    expire_date=row["expire_date"],
                    created_at=row["created_at"]
                )
                for row in cursor.fetchall()
            ]
    
    def is_paid_user(self, user_id: int, group_id: int) -> bool:
        """Check if user is paid and not expired."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT expire_date FROM paid_users
                WHERE user_id = ? AND group_id = ?
            """, (user_id, group_id))
            row = cursor.fetchone()
            
            if row:
                expire_date = datetime.fromisoformat(row["expire_date"])
                return expire_date > datetime.now()
        return False
    
    def remove_paid_user(self, user_id: int, group_id: int) -> bool:
        """Remove a paid user."""
        with self._cursor() as cursor:
            cursor.execute("""
                DELETE FROM paid_users WHERE user_id = ? AND group_id = ?
            """, (user_id, group_id))
            return cursor.rowcount > 0
    
    # ========== Messages Operations ==========
    
    def add_message(self, group_id: int, user_id: int, user_name: str, text: str):
        """Store a message."""
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages (group_id, user_id, user_name, text)
                VALUES (?, ?, ?, ?)
            """, (group_id, user_id, user_name, text))
    
    def get_recent_messages(self, group_id: int, limit: int = 100) -> list[dict]:
        """Get recent messages for a group."""
        with self._cursor() as cursor:
            cursor.execute("""
                SELECT user_name, text, timestamp FROM messages
                WHERE group_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (group_id, limit))
            
            return [
                {
                    "user_name": row["user_name"],
                    "text": row["text"],
                    "timestamp": row["timestamp"]
                }
                for row in cursor.fetchall()
            ][::-1]  # Reverse to chronological order
    
    def clear_messages(self, group_id: int) -> int:
        """Clear messages for a group."""
        with self._cursor() as cursor:
            cursor.execute("DELETE FROM messages WHERE group_id = ?", (group_id,))
            return cursor.rowcount
    
    def trim_messages(self, group_id: int, keep_count: int) -> int:
        """Keep only the most recent N messages for a group.
        
        Args:
            group_id: The group ID
            keep_count: Number of recent messages to keep
            
        Returns:
            Number of messages deleted
        """
        with self._cursor() as cursor:
            # Get IDs of messages to keep (most recent)
            cursor.execute("""
                SELECT id FROM messages 
                WHERE group_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (group_id, keep_count))
            keep_ids = [row["id"] for row in cursor.fetchall()]
            
            if not keep_ids:
                return 0
            
            # Delete all messages not in the keep list
            placeholders = ",".join("?" * len(keep_ids))
            cursor.execute(f"""
                DELETE FROM messages 
                WHERE group_id = ? AND id NOT IN ({placeholders})
            """, [group_id] + keep_ids)
            
            return cursor.rowcount
    
    def get_message_count(self, group_id: int) -> int:
        """Get total message count for a group."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM messages WHERE group_id = ?", (group_id,))
            return cursor.fetchone()["count"]


# Global database instance
db = Database()
