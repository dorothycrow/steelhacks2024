from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement= True)
    username = mapped_column(String(24), nullable=False)
    state = mapped_column(String(64), nullable=False) 
    county = mapped_column(String(64), nullable=False)
    registered = mapped_column(Integer, nullable=False) #1 for yes, 0 for not registered

    
    def __init__(self, username, state, county, registered):
        self.username = username
        self.state = state
        self.county = county
        self.registered = registered
        
    def __repr__(self):
        return "<user {}>".format(self.username)