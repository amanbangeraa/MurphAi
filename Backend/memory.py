import sqlite3
import os
import time
import logging
from threading import Lock
from contextlib import contextmanager
from typing import List, Tuple, Optional
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DB_PATH = "database/memory.db"
MODEL_NAME = "llama-3.3-70b-versatile"  # Default model
MAX_MEMORY_ENTRIES = 10
MAX_RETRY_ATTEMPTS = 5
RETRY_DELAY = 0.1

# Hardcoded API key (for development/testing only)
API_KEY = "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"  # Replace with your actual API key

db_lock = Lock()

class DatabaseError(Exception):
    """Custom exception for database errors"""

@contextmanager
def db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("PRAGMA busy_timeout = 5000")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise DatabaseError(f"Database operation failed: {str(e)}") from e
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize database with proper schema and indexes"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        with db_connection() as conn:
            cursor = conn.cursor()
            # Create main table for conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create table for personal information
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personal_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_role ON conversations(role)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_key ON personal_info(key)")
            conn.commit()
            
            # Validate schema
            cursor.execute("PRAGMA quick_check")
            result = cursor.fetchone()
            if result[0] != "ok":
                raise DatabaseError(f"Database integrity check failed: {result[0]}")
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise DatabaseError("Failed to initialize database") from e
    
def save_personal_info(key: str, value: str) -> None:
    """Save personal information to the database."""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO personal_info (key, value) 
                VALUES (?, ?)
            """, (key.lower(), value))
            conn.commit()
            logger.info(f"Saved personal info: {key} = {value}")
    except sqlite3.Error as e:
        logger.error(f"Failed to save personal info: {str(e)}")
        raise DatabaseError("Failed to save personal info") from e

def get_personal_info(key: str) -> Optional[str]:
    """Retrieve personal information from the database."""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value 
                FROM personal_info 
                WHERE key = ?
            """, (key.lower(),))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve personal info: {str(e)}")
        return None
    
def save_message(role: str, content: str) -> None:
    """Save message to database with retry logic"""
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO conversations (role, content) VALUES (?, ?)",
                    (role.lower(), content)
                )
                conn.commit()
                return
        except sqlite3.OperationalError as e:
            if attempt == MAX_RETRY_ATTEMPTS - 1:
                logger.error("Max retry attempts reached for save_message")
                raise
            time.sleep(RETRY_DELAY)
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error: {str(e)}")
            raise DatabaseError("Invalid data format") from e

def load_memory(limit: int = MAX_MEMORY_ENTRIES) -> str:
    """Load conversation history as formatted string"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content 
                FROM conversations 
                ORDER BY timestamp ASC 
                LIMIT ?
            """, (limit,))
            messages = cursor.fetchall()
            return "\n".join([f"{role}: {content}" for role, content in messages])
    except sqlite3.Error as e:
        logger.error(f"Failed to load memory: {str(e)}")
        return ""

def find_relevant_data(query: str) -> Optional[str]:
    """Find most recent relevant bot response"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content 
                FROM conversations 
                WHERE role = 'assistant' 
                AND content LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (f"%{query}%",))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Search failed: {str(e)}")
        return None

def get_answer(question: str) -> str:
    """Generate AI response with context."""
    try:
        # Check for personal information
        if "my name" in question.lower():
            name = get_personal_info("name")
            if name:
                return f"Your name is {name}."

        # Check for cached response
        cached_response = find_relevant_data(question)
        if cached_response:
            return cached_response

        # Prepare conversation context
        memory = load_memory()
        prompt = f"""Continue this conversation naturally. Respond as a helpful assistant.

        {memory}
        User: {question}
        Assistant: """

        # Generate new response
        client = Groq(api_key=API_KEY)  # Use hardcoded API key
        answer = ""
        
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
            for chunk in completion:
                answer += chunk.choices[0].delta.content or ""
        except Exception as api_error:
            logger.error(f"API call failed: {str(api_error)}")
            answer = "I'm having trouble responding right now. Please try again later."

        # Save conversation
        save_message("user", question)
        save_message("assistant", answer)

        return answer
    except Exception as e:
        logger.error(f"Error in get_answer: {str(e)}")
        return "An error occurred while processing your request."
    
def update_personal_info(question: str) -> Optional[str]:
    """Update personal information based on user input."""
    if "my name is" in question.lower():
        name = question.lower().split("my name is")[1].strip()
        save_personal_info("name", name)
        return f"Got it! I'll remember your name is {name}."
    return None

def memory_agent(query: str) -> Optional[str]:
    """Memory Agent that checks the database for relevant information."""
    # Check for personal information
    if "my name" in query.lower():
        name = get_personal_info("name")
        if name:
            return f"Your name is {name}."

    # Check for cached response
    cached_response = find_relevant_data(query)
    if cached_response:
        return cached_response

    return None

# Initialize database on import
init_db()