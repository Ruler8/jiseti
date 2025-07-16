from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  

    records = db.relationship('Record', backref='user', lazy=True, cascade="all, delete-orphan")

    def is_admin(self):
        return self.role == 'admin'

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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
            "user_id": self.user_id,
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
