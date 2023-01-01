from flask import Blueprint, request, render_template, flash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

def loaddb():
    users = User.query.all()
    print(users) 
    
    for everyuser in users:
        if everyuser.student_id is not None:
            print("ID:" + str(everyuser.id),
            " STD ID:" + everyuser.student_id, 
            " EV ID:" + everyuser.event_id,
            " GR LV:" + everyuser.grade_level)

        else:
            print(everyuser)
            print("is none") 

@auth.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        event_id = request.form.get('event_id')
        grade_level = request.form.get('grade_level')
        print(student_id)
        print(event_id)
        print(grade_level)
        new_user = User(student_id=student_id, event_id=event_id, grade_level=grade_level)
        db.session.add(new_user)
        db.session.commit()
        
        #flash('Account created!', category='success')
        print('Field writen to DB')
        user = User.query.filter_by(student_id=student_id).first()

        print('Event ID:' + user.event_id, ' Grade Level:'  + user.grade_level)       

        # following just prints all users to check if they were written
        #users = User.query.all()
        #print(users) 

        #for everyuser in users:
            #print(everyuser.student_id, everyuser.event_id)

        #print(student_id)
    #if request.method == 'GET':
        #student_id = request.form.get('student_id')
       # event_id = request.form.get('event_id')
        #grade_level = request.form.get('grade_level')
       # user = User.query.filter_by(grade_level=9)
        return render_template("home.html")
 
    #return "<p>home</p>"
    
@auth.route("/login", methods=['GET'])
def login():
    print('IN LOGIN')
    if request.method == 'GET':
        loaddb()

    return "<p>login</p>"

@auth.route('/reports', methods=['GET', 'POST'])
def reports():
    if request.method == 'POST':
       #student_id = request.form.get('student_id')
       #event_id = request.form.get('event_id')
        grade_level = request.form.get('grade_level')
        print('Grade level selected for report is:' + grade_level)

        filteredUsers = User.query.filter_by(grade_level=grade_level).all()
        items = []
        for eachuser in filteredUsers:
            print(eachuser.student_id, eachuser.event_id)
            each_item = []
            each_item.append(eachuser.student_id)
            each_item.append(eachuser.event_id)
            items.append(each_item)

        return render_template("reports.html", text=items)
    else:
        return render_template("reports.html") 
    #return "<p>reports</p>"

@auth.route('/rewards', methods =['GET', 'POST'])
def rewards():
    print('rewards')
    if request.method == 'GET':
        filteredUsers2  = User.query.filter_by(student_id='joe').all()
        for everyuser in filteredUsers2:
            print(everyuser.student_id, everyuser.event_id)
        
        points = User.query.filter_by(student_id='joe').count()
        print('Points are:' + str(points))
    
    return render_template("rewards.html", text3="rewards", points = points)