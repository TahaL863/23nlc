from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
db = SQLAlchemy()
DB_NAME = "database.db"
PHOTO_FOLDER = os.path.join('static')
filename = ""

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tahas first key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' 
    app.config['UPLOAD_FOLDER'] = PHOTO_FOLDER
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'northcreek.jpeg')
    print(filename)

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



       