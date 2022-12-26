from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route("/")
def home():
    return "<p>home</p>"
    
@auth.route("/login")
def login():
    return "<p>login</p>"



