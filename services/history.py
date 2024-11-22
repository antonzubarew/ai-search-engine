import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

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
        except Exception as e:
            logger.error(f"Error adding search to history: {str(e)}")
            self.session.rollback()

    def get_recent_searches(self, limit: int = 10):
        try:
            searches = self.session.query(SearchHistory)\
                .order_by(SearchHistory.created_at.desc())\
                .limit(limit)\
                .all()
            return [{'query': s.query, 'created_at': s.created_at} for s in searches]
        except Exception as e:
            logger.error(f"Error getting search history: {str(e)}")
            return []

    def delete_search(self, search_id: int):
        try:
            search = self.session.query(SearchHistory).get(search_id)
            if search:
                self.session.delete(search)
                self.session.commit()
        except Exception as e:
            logger.error(f"Error deleting search: {str(e)}")
            self.session.rollback()

