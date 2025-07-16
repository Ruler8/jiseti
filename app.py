from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models import db
from routes import register_routes

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jiseti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'  
app.config['JWT_SECRET_KEY'] = 'super-jwt-secret'  

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
