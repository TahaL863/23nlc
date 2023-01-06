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
        spacecheck=student_name.split()
        # print(spacecheck)
        # print('Len:' + str(len(spacecheck)))
        # print(student_name.isalpha())

        # Name validation
        if len(spacecheck) == 2 and spacecheck[0].isalpha() and spacecheck[1].isalpha():
            flash('Entry inputed', category='success')
            new_user = User(student_name=student_name, event_name=event_name, grade_level=grade_level)
            db.session.add(new_user)
            db.session.commit()
        
            print('Field written to DB')
            user = User.query.filter_by(student_name=student_name).first()

            print('Event ID:' + user.event_name, ' Grade Level:'  + user.grade_level)
        else:
            flash('student name must be alphabetic and have one space in between', category='error')           
    return render_template("home.html")
     
@auth.route("/login", methods=['GET'])
def login():
    print('IN LOGIN')
    if request.method == 'GET':
        loaddb()

    return "<p>We will introduce log in ability to portal in future. Press back in browser </p>"

@auth.route('/reports', methods=['GET','POST'])
def reports():
    if request.method == 'POST':
        #grade_level = request.form.get('grade_level')
        grade_level = request.form.get('grades_field')
        print('Grade level selected for report is:' + str(grade_level))
    else:
        grade_level = None

    # logic for calculating points
    # for each unique student
    # query filter by student id and count should be its points
    uniqueStudentList = User.query.with_entities(User.student_name, User.grade_level).distinct()

    studentPointsList=[]

    for eachUStd in uniqueStudentList:
        #print(eachUStd)
        # not grade level means it was empty
        if grade_level is None or not grade_level or eachUStd.grade_level == grade_level:
            pointsPerStudent = User.query.filter_by(student_name=eachUStd.student_name).count()
            eachStudentPoint = []
            eachStudentPoint.append(eachUStd.student_name)
            eachStudentPoint.append(eachUStd.grade_level)
            eachStudentPoint.append(pointsPerStudent)
            studentPointsList.append(eachStudentPoint)
    
    # sort results by grade
    studentPointsList.sort(key=lambda eachStudentPoint: eachStudentPoint[1], reverse=True)
    #print(studentPointsList)

    gradesInputList = [9, 10, 11]
    return render_template("reports.html", studentView=studentPointsList, gradesInput=gradesInputList)

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
                    prizeComment="you won the Gold Medal"
                elif pointsforreward >= 4 and pointsforreward < 7:
                    prizeComment="you won pizza"
                elif pointsforreward >= 1 and pointsforreward < 4:
                    prizeComment="you won a North Creek tshirt"

                eachp.append(prizeComment)
                print(eachp)
                highestPbyGradeList.append(eachp)

        return highestPbyGradeList


@auth.route('/rewards', methods =['GET', 'POST'])
def rewards():
    print('rewards')
        
    highestPbyGradeList = get_rewards()
                               
    if request.method == 'POST':
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
            
                winnerList = []
                eachWinner = []
                eachWinner.append(euser.student_name)
                eachWinner.append(euser.grade_level)
                
                points = User.query.filter_by(student_name=euser.student_name).count()
                eachWinner.append(points)
                winnerList.append(eachWinner)
                #print(points)
                if points >= 7:
                    rewardsString = "you won the Gold Medal"        
                elif points >= 4 and points < 7:
                    rewardsString = "you won pizza"
                elif points >= 1 and points < 4:
                    rewardsString = "you won a North Creek tshirt"
                return render_template("rewards.html", highestPbyGrades=highestPbyGradeList, winner=winnerList, reward=rewardsString)

    return render_template("rewards.html", highestPbyGrades=highestPbyGradeList)

      
