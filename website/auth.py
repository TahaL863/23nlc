from flask import Blueprint, request, render_template, flash
from .models import User
from . import db, filename
import random, os
auth = Blueprint('auth', __name__)
from apscheduler.schedulers.blocking import BlockingScheduler

eventsInputList = ["basketball", "football", "soccer", "baseball", "track",
                    "coding", "writing", "speech", "music", "art"]

# Used to add students who can be in any high school grade
static_grade_set = ["9", "10", "11", "12"]

# these are global so they get populated with scheduler task as well
highestPbyGradeList = []
grade_dict = {}

def loaddb():
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

def scheduler_func():
    highestPbyGradeList, grade_dict = get_highestPointsByGrade()
    print('scheduler executed')
 

@auth.route('/', methods=['GET'])
def reports_scheduler():
    print('Scheduler initialized')
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduler_func(), 'interval', seconds=10) 
    #hours=0.017)
    scheduler.start()
    return render_template("home.html", userimage = filename)

@auth.route("/login", methods=['GET'])
def login():
    if request.method == 'GET':
        loaddb()
    return render_template("login.html", message="Under Construction - We will introduce login ability to portal in future.")    
       
@auth.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        event_name = request.form.get('event_name')
        grade_selected = request.form.get('grades_field')
        spacecheck=student_name.split()

        # Name validation
        if len(spacecheck) == 2 and spacecheck[0].isalpha() and spacecheck[1].isalpha():
            flash('Sudent successfully added', category='success')
            new_user = User(student_name=student_name, event_name=event_name, grade_level=grade_selected)
            db.session.add(new_user)
            db.session.commit()
        
            print('Field written to DB')
            user = User.query.filter_by(student_name=student_name).first()

            print('Event ID:' + user.event_name, ' Grade Level:'  + user.grade_level)
        else:
            flash('student name must be alphabetic and have one space in between', category='error')           
    return render_template("addstudent.html", eventsInput=eventsInputList, gradesInput=static_grade_set)


@auth.route('/reports', methods=['GET','POST'])
def reports():
    if request.method == 'POST':
        grade_level = request.form.get('grades_field')

        if grade_level is None or grade_level == "":
            flash('No grade selected', category='success')
        else:
            flash('Grade level selected is ' + grade_level, category='success')

    else:
        grade_level = None

    # logic for calculating points
    # for each unique student
    # query filter by student id and count should be its points
    uniqueStudentList = User.query.with_entities(User.student_name, User.grade_level).distinct()

    studentPointsList=[]

    # Used to dynamically store unique grades for which we have students and use it in drop downs
    grade_set = {}

    for eachUStd in uniqueStudentList:

        if eachUStd.grade_level not in grade_set.keys():
            grade_set[eachUStd.grade_level] = eachUStd.grade_level
        
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
    return render_template("reports.html", studentView=studentPointsList, gradesInput=grade_set)

def get_highestPointsByGrade():

        # query every distinct user by student id
        distinctUsers = User.query.with_entities(User.student_name, User.grade_level).distinct()

        pointsList = []
        for everyduser in distinctUsers:
        
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
        
        pointsList.sort(key=lambda each_item: each_item[2], reverse=True)

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
                    prizeComment="you won a Pizza"
                elif pointsforreward >= 1 and pointsforreward < 4:
                    prizeComment="you won a North Creek T-shirt"

                eachp.append(prizeComment)
                #print(eachp)
                highestPbyGradeList.append(eachp)

        return highestPbyGradeList, grade_dict


@auth.route('/rewards', methods =['GET', 'POST'])
def rewards():
    print('rewards')
    # Display when there was only a single student in class who was already highest winner
    noRandomElement = ""

    # this call is also made from scheduler which computes non UI reports and displays them once one proceeds to reports page
    highestPbyGradeList, grade_dict = get_highestPointsByGrade()

    if request.method == 'POST':
        grade_level = request.form.get('grade_level')
        flash('Grade level selected is ' + grade_level, category='success')
        maxUsersByGrade = User.query.filter_by(grade_level=grade_level).count()
        print('MaxUsersByGrade:' + str(maxUsersByGrade))

        random_number = random.randint(1, maxUsersByGrade)
        print('Random number selected is:' + str(random_number))

        allUsersInSelectedGrade = User.query.filter_by(grade_level=grade_level).all()

        # print("All users in selected grade")
        # print(allUsersInSelectedGrade)

        # for a in allUsersInSelectedGrade:
        #     print(a.student_name + " ", a.grade_level)

        unique_user_dict = {}
        highestScoreStudent = ""

        for euser in allUsersInSelectedGrade:

            # if seeing user for the first time
            if euser.student_name not in unique_user_dict.keys():
                unique_user_dict[euser.student_name] = euser.student_name

                # Random picked one' can't be the highest user (unless its the only user in that grade) so pick the next one
                for evry_std in highestPbyGradeList:
                    #print("Each user in Curr Grade:" + euser.student_name  + " highPbyGradeList: " + evry_std[0])
                    if maxUsersByGrade > 1 and euser.student_name == evry_std[0]:
                        highestScoreStudent = euser.student_name 
                        break
        
        counter = 0
        for key in unique_user_dict:
            if key != highestScoreStudent and highestScoreStudent != "":
                counter = counter +1
                if counter == (random_number%len(unique_user_dict)):
                    winnerList = []
                    eachWinner = []
                    eachWinner.append(key)
                    eachWinner.append(grade_level)
                
                    points = User.query.filter_by(student_name=key).count()
                    eachWinner.append(points)
                    winnerList.append(eachWinner)
                    #print(points)
                    if points >= 7:
                        rewardsString = "you won the Gold Medal"        
                    elif points >= 4 and points < 7:
                        rewardsString = "you won a Pizza"
                    elif points >= 1 and points < 4:
                        rewardsString = "you won a North Creek T-shirt"
                    return render_template("rewards.html", highestPbyGrades=highestPbyGradeList, gradesInput=grade_dict, winner=winnerList, reward=rewardsString)
        noRandomElement = 'Could not find a second winner to choose as random'

    return render_template("rewards.html", highestPbyGrades=highestPbyGradeList,gradesInput=grade_dict, noRandomElement=noRandomElement)

@auth.route('/help', methods=['GET', 'POST'])
def help():
    return render_template("help.html")

@auth.route('/remove', methods=['GET', 'POST'])
def remove():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        event_name = request.form.get('event_name')
        grade_level = request.form.get('grade_level')
        checker = User.query.filter_by(student_name=student_name).count()
        #checker2 = User.query.filter_by(event_name=event_name).count()
        #checker3 = User.query.filter_by(grade_level=event_name).count()
        if checker >= 1:
            #event_name = request.form.get('event_name')
            #User.query.filter_by(student_name=student_name):
            #grade_level = request.form.get('grade_level')
            User.query.filter_by(student_name=student_name, event_name=event_name, grade_level=grade_level).delete()
            db.session.commit()
            flash('Entry removed', category='success')
            #return render_template("remove.html")
        else:    
            flash('Entry not found', category='error')
    return render_template("remove.html")
