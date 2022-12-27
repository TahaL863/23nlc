from flask import Blueprint, request, render_template
auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def home():
 
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        event_id = request.form.get('event_id')
        print(student_id)
        print(event_id)
    
        return render_template("home.html")
    #return "<p>home</p>"
    
@auth.route("/login")
def login():
    return "<p>login</p>"



