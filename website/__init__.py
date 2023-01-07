from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tahas first key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' 
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()       
        print('Created or updated Database!')

    return app



       