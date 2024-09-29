from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean

# Initialize SQLAlchemy without an app instance
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'  # Specify the table name explicitly

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    fName = db.Column(String(64), nullable=False)
    lName = db.Column(String(64), nullable=False)
    address = db.Column(String(64), nullable=False)
    city = db.Column(String(64), nullable=False)
    state = db.Column(String(64), nullable=False)
    county = db.Column(String(64), nullable=False)
    zipcode = db.Column(String(20), nullable=False)
    dob = db.Column(String(20), nullable=False)
    registered = db.Column(Boolean, nullable=False)
    gameBadge = db.Column(Boolean, nullable=False)
    

    def __init__(self, fName, lName, address, city, state, county, zipcode, dob, registered, gameBadge):
        self.fName = fName
        self.lName = lName
        self.address = address
        self.city = city
        self.state = state
        self.county = county
        self.zipcode = zipcode
        self.dob = dob
        self.registered = registered
        self.gameBadge = gameBadge

    def __repr__(self):
        return "<user {}>".format(self.username)