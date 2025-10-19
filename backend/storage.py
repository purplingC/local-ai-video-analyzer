import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure local persistent folder
os.makedirs("data", exist_ok=True)

DB_PATH = "data/chat_history.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(32))  # user / assistant / system
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)  # store in UTC


def init_db():
    """Initialize the SQLite database and create required tables."""
    Base.metadata.create_all(bind=engine)


def save_message(role: str, text: str):
    # Save all message (user/assistant/system)
    db = SessionLocal()
    try:
        msg = ChatMessage(role=role, text=text, timestamp=datetime.utcnow())  # store UTC
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg.id
    except Exception as e:
        print(f"[DB] Error saving message: {e}")
    finally:
        db.close()


def get_recent(n: int = 100):
    # Get last N messages in ascending order
    db = SessionLocal()
    try:
        rows = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).limit(n).all()
        messages = []
        for r in reversed(rows):
            # Convert UTC to Malaysia Time (UTC+8)
            malaysia_time = (r.timestamp + timedelta(hours=8)).strftime("%d %b %Y, %I:%M %p MYT")
            messages.append({
                "id": r.id,
                "role": r.role,
                "text": r.text,
                "timestamp": malaysia_time
            })
        return messages
    finally:
        db.close()


def clear_all_history():
    db = SessionLocal()
    try:
        count = db.query(ChatMessage).delete()
        db.commit()
        return count
    finally:
        db.close()
