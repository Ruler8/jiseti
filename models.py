from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class NormalUser(db.Model):
    __tablename__ = 'normal_users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    records = db.relationship('Record', backref='normal_user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NormalUser {self.name}>"

class Administrator(db.Model):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin_number = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Administrator {self.name}, AdminNumber={self.admin_number}>"

class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="draft")  
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link only to normal users
    normal_user_id = db.Column(db.Integer, db.ForeignKey('normal_users.id'), nullable=False)

    media = db.relationship("Media", backref="record", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "normal_user_id": self.normal_user_id,
            "created_at": self.created_at.isoformat(),
            "media": [m.to_dict() for m in self.media]
        }

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String, nullable=True)
    video_url = db.Column(db.String, nullable=True)
    record_id = db.Column(db.Integer, db.ForeignKey("records.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "video_url": self.video_url,
            "record_id": self.record_id
        }
