from flask import Blueprint, request, render_template, flash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

def loaddb():
    users = User.query.all()
    #print(users) 

    for everyuser in users:
        if everyuser.student_id is not None:
            print("ID " + str(everyuser.id),
            " STD ID " + everyuser.student_id, 
            "EV ID" + everyuser.event_id)
        else:
            print(everyuser)
            print("is none") 

@auth.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        event_id = request.form.get('event_id')
        print(student_id)
        print(event_id)
        new_user = User(student_id=student_id, event_id=event_id)
        db.session.add(new_user)
        db.session.commit()
        
        #flash('Account created!', category='success')
        print('Field writen to DB')
        user = User.query.filter_by(student_id=student_id).first()

        print('This is my user id '  + user.event_id)       

        # following just prints all users to check if they were written
        #users = User.query.all()
        #print(users) 

        #for everyuser in users:
            #print(everyuser.student_id, everyuser.event_id)

        #print(student_id)
        return render_template("home.html")
 
    #return "<p>home</p>"
    
@auth.route("/login", methods=['GET'])
def login():
    print('IN LOGIN')
    if request.method == 'GET':
        loaddb()

    return "<p>login</p>"



