from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import validates

from app import db

class Views(db.Model):
    __tablename__ = 'views'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete="CASCADE"))
    Bookmark = Column(Boolean)


    def __str__(self):
        return self.name

class Projects(db.Model):
    __tablename__ = 'projects'
    project_id = Column(Integer, primary_key=True)
    project_name = Column(String(30))
    status = Column(String(50))
    tag = Column(String(50))
    start_date= Column(DateTime)

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"

class Items(db.Model):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete="CASCADE"))
    amount = Column(Integer)
    type = Column(String(50))
    category = Column(String(50))
    start_date= Column(DateTime)

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"
