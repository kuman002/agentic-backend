"""
Meeting management module for scheduling and querying meetings.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, Meeting
from datetime import datetime
from typing import List, Optional

def create_meeting(
    title: str,
    start_time: str,
    description: Optional[str] = None,
    db: Optional[Session] = None
) -> dict:
    """
    Create a new meeting in the database.
    
    Args:
        title: Meeting title
        start_time: Meeting start time (format: YYYY-MM-DD HH:MM)
        description: Optional meeting description
        db: Database session (creates new if not provided)
    
    Returns:
        Dictionary with created meeting details
    """
    if db is None:
        db = SessionLocal()
    
    try:
        meeting = Meeting(
            title=title,
            start_time=start_time,
            description=description or ""
        )
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        return {
            "id": meeting.id,
            "title": meeting.title,
            "start_time": meeting.start_time,
            "description": meeting.description
        }
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create meeting: {str(e)}")
    finally:
        db.close()

def get_all_meetings(db: Optional[Session] = None) -> List[dict]:
    """
    Retrieve all meetings from the database.
    
    Args:
        db: Database session (creates new if not provided)
    
    Returns:
        List of meeting dictionaries
    """
    if db is None:
        db = SessionLocal()
    
    try:
        meetings = db.query(Meeting).all()
        return [
            {
                "id": m.id,
                "title": m.title,
                "start_time": m.start_time,
                "description": m.description
            }
            for m in meetings
        ]
    except Exception as e:
        raise Exception(f"Failed to retrieve meetings: {str(e)}")
    finally:
        db.close()

def get_meeting_by_id(meeting_id: int, db: Optional[Session] = None) -> Optional[dict]:
    """
    Retrieve a specific meeting by ID.
    
    Args:
        meeting_id: Meeting ID
        db: Database session (creates new if not provided)
    
    Returns:
        Meeting dictionary or None if not found
    """
    if db is None:
        db = SessionLocal()
    
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            return {
                "id": meeting.id,
                "title": meeting.title,
                "start_time": meeting.start_time,
                "description": meeting.description
            }
        return None
    except Exception as e:
        raise Exception(f"Failed to retrieve meeting: {str(e)}")
    finally:
        db.close()

def update_meeting(
    meeting_id: int,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    description: Optional[str] = None,
    db: Optional[Session] = None
) -> dict:
    """
    Update an existing meeting.
    
    Args:
        meeting_id: Meeting ID
        title: New title (if provided)
        start_time: New start time (if provided)
        description: New description (if provided)
        db: Database session (creates new if not provided)
    
    Returns:
        Updated meeting dictionary
    """
    if db is None:
        db = SessionLocal()
    
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise Exception(f"Meeting {meeting_id} not found")
        
        if title:
            meeting.title = title
        if start_time:
            meeting.start_time = start_time
        if description is not None:
            meeting.description = description
        
        db.commit()
        db.refresh(meeting)
        
        return {
            "id": meeting.id,
            "title": meeting.title,
            "start_time": meeting.start_time,
            "description": meeting.description
        }
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to update meeting: {str(e)}")
    finally:
        db.close()

def delete_meeting(meeting_id: int, db: Optional[Session] = None) -> bool:
    """
    Delete a meeting from the database.
    
    Args:
        meeting_id: Meeting ID
        db: Database session (creates new if not provided)
    
    Returns:
        True if deleted, False if not found
    """
    if db is None:
        db = SessionLocal()
    
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return False
        
        db.delete(meeting)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to delete meeting: {str(e)}")
    finally:
        db.close()

def search_meetings(query: str, db: Optional[Session] = None) -> List[dict]:
    """
    Search meetings by title or description.
    
    Args:
        query: Search query string
        db: Database session (creates new if not provided)
    
    Returns:
        List of matching meeting dictionaries
    """
    if db is None:
        db = SessionLocal()
    
    try:
        meetings = db.query(Meeting).filter(
            (Meeting.title.ilike(f"%{query}%")) |
            (Meeting.description.ilike(f"%{query}%"))
        ).all()
        
        return [
            {
                "id": m.id,
                "title": m.title,
                "start_time": m.start_time,
                "description": m.description
            }
            for m in meetings
        ]
    except Exception as e:
        raise Exception(f"Failed to search meetings: {str(e)}")
    finally:
        db.close()

def count_meetings(db: Optional[Session] = None) -> int:
    """
    Count total number of meetings.
    
    Args:
        db: Database session (creates new if not provided)
    
    Returns:
        Total meeting count
    """
    if db is None:
        db = SessionLocal()
    
    try:
        return db.query(Meeting).count()
    except Exception as e:
        raise Exception(f"Failed to count meetings: {str(e)}")
    finally:
        db.close()

def format_meeting_list(meetings: List[dict]) -> str:
    """
    Format meetings list for display.
    
    Args:
        meetings: List of meeting dictionaries
    
    Returns:
        Formatted string representation
    """
    if not meetings:
        return "No meetings found."
    
    output = "Scheduled Meetings:\n" + "=" * 50 + "\n"
    for i, m in enumerate(meetings, 1):
        output += f"{i}. {m['title']} at {m['start_time']}\n"
        if m['description']:
            output += f"   Description: {m['description']}\n"
    
    return output
