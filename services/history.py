import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

from sqlalchemy.dialects.postgresql import JSON

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class SearchResults(Base):
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False)
    ai_response = Column(String, nullable=False)
    raw_results = Column(JSON, nullable=False)

class HistoryService:
    def __init__(self):
        self.engine = create_engine(os.environ['DATABASE_URL'])
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_search(self, query: str):
        try:
            search = SearchHistory(query=query)
            self.session.add(search)
            self.session.commit()
            return search
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding search to history: {str(e)}")
            return None

    def get_recent_searches(self, limit: int = 10):
        try:
            searches = self.session.query(SearchHistory)\
                .order_by(SearchHistory.created_at.desc())\
                .limit(limit)\
                .all()
            return [{'id': s.id, 'query': s.query, 'created_at': s.created_at} for s in searches]
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error getting search history: {str(e)}")
            return []

    def delete_search(self, search_id: int):
        try:
            search = self.session.query(SearchHistory).get(search_id)
            if search:
                self.session.delete(search)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting search: {str(e)}")
            return False

    def save_search_results(self, search_id: int, ai_response: str, raw_results: list):
        try:
            from sqlalchemy import text
            stmt = text("INSERT INTO search_results (search_id, ai_response, raw_results) VALUES (:search_id, :ai_response, :raw_results)")
            self.session.execute(stmt, {
                'search_id': search_id,
                'ai_response': ai_response,
                'raw_results': raw_results
            })
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving search results: {str(e)}")
            return False

    def get_search_results(self, search_id: int):
        try:
            from sqlalchemy import text
            stmt = text("SELECT ai_response, raw_results FROM search_results WHERE search_id = :search_id")
            result = self.session.execute(stmt, {'search_id': search_id}).first()
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting search results: {str(e)}")
            return None

    def get_last_search(self):
        try:
            return self.session.query(SearchHistory).order_by(SearchHistory.id.desc()).first()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error getting last search: {str(e)}")
            return None
