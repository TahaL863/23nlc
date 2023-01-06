from flask import Blueprint, request, render_template, flash
from .models import User
from . import db
import random
auth = Blueprint('auth', __name__)
from apscheduler.schedulers.blocking import BlockingScheduler

def loaddb():
    #reports_scheduler()
    users = User.query.all()
    print(users) 
    
    for everyuser in users:
        if everyuser.student_name is not None:
            print("ID:" + str(everyuser.id),
            " STD Name:" + everyuser.student_name, 
            " EV Name:" + everyuser.event_name,
            " GR LV:" + everyuser.grade_level)

        else:
            print(everyuser)
            print("is none") 

def reports_scheduler():
    print('Scheduler initialized')
    scheduler = BlockingScheduler()
    scheduler.add_job(get_rewards(), 'interval', seconds=10) 
    #hours=0.017)
    scheduler.start()

@auth.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        event_name = request.form.get('event_name')
        grade_level = request.form.get('grade_level')
        print(student_name)
        print(event_name)
        print(grade_level)
        new_user = User(student_name=student_name, event_name=event_name, grade_level=grade_level)
        db.session.add(new_user)
        db.session.commit()
        
        #flash('Account created!', category='success')
        print('Field writen to DB')
        user = User.query.filter_by(student_name=student_name).first()

        print('Event ID:' + user.event_name, ' Grade Level:'  + user.grade_level)       
        return render_template("home.html")
     
@auth.route("/login", methods=['GET'])
def login():
    print('IN LOGIN')
    if request.method == 'GET':
        loaddb()

    return "<p>We will introduce log in ability to portal in future </p>"

@auth.route('/reports', methods=['GET','POST'])
def reports():
    if request.method == 'POST':
        grade_level = request.form.get('grade_level')
        print('Grade level selected for report is:' + grade_level)
    else:
        grade_level = None

    # logic for calculating points
    # for each unique student
    # query filter by student id and count should be its points
    uniqueStudentList = User.query.with_entities(User.student_name, User.grade_level).distinct()

    items=[]

    for eachUStd in uniqueStudentList:
        #print(eachUStd)
        if grade_level is None or eachUStd.grade_level == grade_level:
            pointsPerStudent = User.query.filter_by(student_name=eachUStd.student_name).count()
            each_item = []
            each_item.append(eachUStd.student_name)
            each_item.append(eachUStd.grade_level)
            each_item.append(pointsPerStudent)
            items.append(each_item)
    
    # sort results by grade
    items.sort(key=lambda each_item: each_item[1], reverse=True)
    print(items)
    return render_template("reports.html", text=items)

def get_rewards():
        # query every distinct user by student id
        distinctUsers = User.query.with_entities(User.student_name, User.grade_level).distinct()

        pointsList = []
        for everyduser in distinctUsers:
            #print('Student ID: ' + everyduser.student_name + ' Grade Level:' + everyduser.grade_level)
            #query all rows for each of the above distinct user
            # allentriesPerUser  = User.query.filter_by(student_name = everyduser.student_name).all()
            # for user in allentriesPerUser:
            #     print(user.student_name, user.event_name)
        
            #compile total points for each user
            points = User.query.filter_by(student_name=everyduser.student_name).count()
            eachpoint = []
            eachpoint.append(everyduser.student_name)

            # inserted grade level because we want to report per grade
            eachpoint.append(everyduser.grade_level)
            eachpoint.append(points)
            pointsList.append(eachpoint)
            #print('Points are:' + str(points))
        
        # telling sort to use eachpoint[2] which is 2nd field called points as the sorting criteria
        sorted(pointsList, key=lambda eachpoint: eachpoint[2])
        pointsList.sort(key=lambda each_item: each_item[2], reverse=True)
        #items.sort(key=lambda each_item: each_item[1], reverse=True)

        # dictionary to see if we already found highest points for that grade
        grade_dict = {}
        highestPbyGradeList = []
      
        for eachp in pointsList:

            if eachp[1] not in grade_dict.keys():
                grade_dict[eachp[1]] = eachp[1]

                pointsforreward = eachp[2]
                if pointsforreward >= 7: 
                    prizeComment="you won first place"
                elif pointsforreward >= 4 and points < 7:
                    prizeComment="you won second place"
                elif pointsforreward >= 1 and points < 4:
                    prizeComment="you won third place"

                eachp.append(prizeComment)
                print(eachp)
                highestPbyGradeList.append(eachp)

        return highestPbyGradeList


@auth.route('/rewards', methods =['GET', 'POST'])
def rewards():
    print('rewards')
    if request.method == 'GET':
        highestPbyGradeList = get_rewards()
        return render_template("rewards.html", text3="rewards", elected_grade = highestPbyGradeList)
                               
    elif request.method == 'POST':
        grade_level = request.form.get('grade_level')
        maxUsersByGrade = User.query.filter_by(grade_level=grade_level).count()
        # print('MaxUsersByGrade:' + str(maxUsersByGrade))

        random_number = random.randint(1, maxUsersByGrade)
        # print('Random number selected is:' + str(random_number))

        allUsersInSelectedGrade = User.query.filter_by(grade_level=grade_level).all()

        counter = 1
        for euser in allUsersInSelectedGrade:
            if counter < random_number:
                counter = counter+1
            elif counter == random_number:
            
                winnerList = [euser.student_name, euser.grade_level]   
                
                filteredUsers = User.query.filter_by(student_name=euser.student_name).count()
                points = filteredUsers
                print(points)
                if points >= 7:
                    return render_template("rewards.html", winner=winnerList, reward1 = "you won first place")        
                elif points >= 4 and points < 7:
                    return render_template("rewards.html", winner=winnerList, reward2 = "you won second place")
                elif points >= 1 and points < 4:
                    return render_template("rewards.html", winner=winnerList, reward3 = "you won third place")
        return render_template("rewards.html")

      
