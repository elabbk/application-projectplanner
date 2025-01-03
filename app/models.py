from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import validates

from .db import db


class Views(db.Model):
    __tablename__ = 'views'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete="CASCADE"))
    bookmark = Column(Boolean)
    read = Column(Boolean)
    write = Column(Boolean)
    delete  = Column(Boolean)
    archive  = Column(Boolean)

    def __str__(self):
        return self.name

class Projects(db.Model):
    __tablename__ = 'projects'
    project_id = Column(Integer, primary_key=True)
    project_name = Column(String(30))
    status = Column(String(50))
    tag = Column(String(50))
    proj_start_date= Column(DateTime)
    proj_end_date = Column(DateTime)

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"

class Items(db.Model):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(100))
    type = Column(String(50))
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete="CASCADE"))
    amount = Column(Integer)
    category = Column(String(50))
    item_tag = Column(String(50))
    item_start_date= Column(DateTime)
    item_end_date = Column(DateTime)

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"
