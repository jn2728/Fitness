import string
from app import app, db
from flask import Flask, render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user, login_user, logout_user
from app.forms import RegistrationForm, LoginForm, Image1Form, Image2Form, BMRForm, ReflectionForm, workoutForm, CalForm
from app.models import User, Before, After, Reflection, Workout, Calories, Bmr
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import sqlite3 as sql
import sys
import random

# Global variables used for new users
New = 0
image1 = 0
image2 = 0
bmrField = 0
calField = 0

# Upload folder for images in flask static
UPLOAD_FOLDER = 'app/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# index if unauthorized and hub if authorized. If new, adding example entries into database
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        global New
        if New == 1:
            New = 0
            # example for reflections entry
            g.user = current_user.get_id()
            Date = "Welcome to Feelin Good!"
            Refl = "Here you will be able to reflect on your growth and view that progress at a later time. Feel free to write anything that motivates you! Good luck!"
            ex_reflection = Reflection(userid = g.user, date = Date, reflection = Refl)
            db.session.add(ex_reflection)
            db.session.commit()
            # example for workouts entry
            Date = "Log a workout"
            bodyP = "Chest"
            Log = "Monday: [chestPress] - [50lbs, 12 Reps] , [incline ChestPress] - [40lbs, 8 Reps]"
            ex_workout = Workout(userid = g.user, date = Date, workout = Log, bodypart = bodyP)
            db.session.add(ex_workout)
            db.session.commit()

        # Random motivational quotes init
        quotes = ["Once you learn to quit, it becomes a habit.***Vince Lombardi Jr", "A feeble body weakens the mind.***Jean-Jacques Rousseau", "The groundwork for all happiness is good health.***Leigh Hunt", \
        "Success is what comes after you stop making excuses.***Luis Galarza", "Discipline is the bridge between goals and accomplishment.***Jim Rohn"]
        # splitting for quote + author
        num = random.randint(0, 4)
        stringy = quotes[num]
        group = []
        group = stringy.split("***")
        quote = group[0]
        author = group[1]
        # hub if authorized
        return render_template('hub/hub.html', quote = quote, author = author)
    # index if not authorized
    return render_template('hub/index.html')

# Registration generates new user and sends info to user table
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        global New, bmrField, calField, image1, image2
        bmrField = 0
        calField = 0 # values reset for new user, New set to 1
        image1 = 0
        image2 = 0
        New = 1
        new_user = User(name = form.username.data, email = form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('user/register.html', form=form)

# Authorizes user and sends them to index
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Login a new user.'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash(('Successfully logged in!',"success"))
            return redirect(url_for("index"))
    return render_template('user/login.html', form=form)

# login checks data for authorization into hub
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    '''Logout the current user.'''
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


# workouts components page
@app.route("/workouts", methods=['GET', 'POST'])
def workouts():
    g.user = current_user.get_id()
    workouts = []
    for work in db.session.query(Workout.date).filter(Workout.userid == g.user):
        workouts.append(work)
    workouts = [i[0] for i in workouts]
    print(workouts)
    return render_template('workouts/workouts.html', workouts=workouts)

#The following allow viewing of all the extension workout pages
@app.route("/workoutAtGym", methods=['GET', 'POST'])
def workoutAtGym():
    return render_template('workouts/workoutAtGym.html')
@app.route("/workoutAtHome", methods=['GET', 'POST'])
def workoutAtHome():
    return render_template('workouts/workoutAtHome.html')
@app.route("/gymBeginner", methods=['GET', 'POST'])
def gymBeginner():
    return render_template('workouts/gymBeginner.html')
@app.route("/gymIntermediate", methods=['GET'])
def gymIntermediate():
    return render_template('workouts/gymIntermediate.html')
@app.route("/gymAdvanced", methods=['GET'])
def gymAdvanced():
    return render_template('workouts/gymAdvanced.html')
@app.route("/homeBeginner", methods=['GET', 'POST'])
def homeBeginner():
    return render_template('workouts/homeBeginner.html')
@app.route("/homeIntermediate", methods=['GET'])
def homeIntermediate():
    return render_template('workouts/homeIntermediate.html')
@app.route("/homeAdvanced", methods=['GET'])
def homeAdvanced():
    return render_template('workouts/homeAdvanced.html')

# Diet page checks for no entries for BMI and calories data and sends to appropriate html version
# data is queried and calculated to provide information about dieting component
@app.route("/diet", methods=['GET', 'POST'])
def diet():
    if int(calField) != 0:
        if int(bmrField) != 0:
            g.user = current_user.get_id()
            tmp = []
            for b in db.session.query(Bmr.bmr).filter(Bmr.userid == g.user):
                tmp.append(b)
            hold = str(tmp[0])

            bmr = hold[1:-2]
            calories = []
            dates = []
            for days in db.session.query(Calories.date).filter(Calories.userid == g.user).all():
                dates.append(days)
            dates = [i[0] for i in dates]
            for cals in db.session.query(Calories.cal4day).filter(Calories.userid == g.user).all():
                calories.append(cals)
            calories = [i[0] for i in calories]

            longerList = zip(dates,calories)
            dsList = []
            for a in longerList:
                if int(a[1] == int(bmr)):
                    dsList.append("=")
                if int(a[1]) > int(bmr):
                    #print(bmr + " " + a[1])
                    store = int(a[1]) - int(bmr)
                    dsList.append("+ " + str(store))

                if int(a[1]) < int(bmr):
                    #print(str(bmr) + " " + str(a[1]))
                    store = int(bmr)- int(a[1])
                    dsList.append("- " + str(store))

            longList = zip(dates,calories,dsList)
            print("test")
            return render_template('diet/diet.html', bigList=list(longList), BMR=bmr)
    #reflections.append(ref)
    #eflections = [i[0] for i in reflections]

    testing = ["","",""]
    print("test1")
    return render_template('diet/dietEmpty.html')

# addCals allows for user to add calories to get info on dieting information tracking
@app.route("/addCals", methods=['GET','POST'])
def addCals():
    global calField
    form = CalForm()
    g.user = current_user.get_id()
    exists = db.session.query(Calories.date).filter(Calories.date == form.date.data).first() is not None
    if form.validate_on_submit():
        if exists:
            db.session.query(Calories).filter(Calories.date == form.date.data).update({'cal4day':form.cals.data})
            db.session.commit()
            return redirect(url_for('diet'))
        new_cals = Calories(userid = g.user, cal4day = form.cals.data, date = form.date.data)
        db.session.add(new_cals)
        db.session.commit()
        calField = 1
        return redirect(url_for('diet'))
    return render_template('diet/addCals.html', form=form)

# addBMR allows for user to add bmr to get info on dieting information tracking
@app.route("/addBMR", methods=['GET','POST'])
def addBMR():
    global bmrField
    form = BMRForm()
    g.user = current_user.get_id()
    exists = db.session.query(Bmr.userid).filter(Bmr.userid == g.user).first() is not None
    if form.validate_on_submit():
        if exists:
            db.session.query(Bmr).filter(Bmr.userid == g.user).update({'bmr':form.BMR.data})
            db.session.commit()
            return redirect(url_for('diet'))
        new_bmr = Bmr(userid = g.user, bmr = form.BMR.data)
        db.session.add(new_bmr)
        db.session.commit()
        bmrField = 1
        return redirect(url_for('diet'))
    return render_template('diet/addBMR.html', form=form)

# Allows for entering a workout process for a day and muscle
@app.route('/workouts/logWorkout',  methods=['GET', 'POST'])
@login_required
def logWorkout():
    form = workoutForm()
    g.user = current_user.get_id()

    if form.validate_on_submit():
        new_workout = Workout(userid = g.user, date = form.date.data, workout = form.workout.data, bodypart = form.bodypart.data)
        db.session.add(new_workout)
        db.session.commit()
        return redirect(url_for('workouts'))
    return render_template('workouts/logWorkout.html', form=form)

# Allows selection of a workout based on filtering from database
@app.route('/workoutSelect', methods=['POST'])
def workoutSelect():
    if request.method == 'POST':
        date = request.form["ref"]

        g.user = current_user.get_id()
        Date = str(db.session.query(Workout.date).filter(Workout.userid == g.user, Workout.date == date).one())
        Date = str(Date)
        Date = Date.replace("(\'","")
        Date = Date.replace("\',)","")

        bodyPart = str(db.session.query(Workout.bodypart).filter(Workout.userid == g.user, Workout.date == date).one())
        bodyPart = str(bodyPart)
        bodyPart = bodyPart.replace("(\'","")
        bodyPart = bodyPart.replace("\',)","")


        Ref = str(db.session.query(Workout.workout).filter(Workout.userid == g.user, Workout.date == date).one())
        Ref = str(Ref)
        Ref = Ref[2:]
        Ref = Ref[0:-3]
        Ref = Ref.replace("\\r\\n", "<br>")


        print(Date,file=sys.stderr)
        print(Ref,file=sys.stderr)

        date = Date
        workout = Ref
        bp = bodyPart

        return render_template('workouts/viewLog.html', date=date, workout=workout, bp = bp)
    return render_template('workouts/workouts.html')

# progression navigations
@app.route("/progression", methods=['GET', 'POST'])
def progression():

    # Getting Reflection Information
    g.user = current_user.get_id()
    reflections = []
    for ref in db.session.query(Reflection.date).filter(Reflection.userid == g.user):
        reflections.append(ref)
    reflections = [i[0] for i in reflections]

    # Getting Before and After Image Information
    default = "###" #for non uploads
    defaultI = "defImg.jpg"
    relPath = "/static/images/"
    dImg = os.path.join(relPath, defaultI)
    if image1 == 0:
        if image2 == 0:
            # here no images rendered
            return render_template('progression/progression.html', bImg=dImg, bWt=default, bDt=default, aImg=dImg, aWt=default, aDt=default, reflections = reflections)
        else:
            # here only image2 rendered
            g.user = current_user.get_id()

            aImg = str(db.session.query(After.img2).filter(After.userid == g.user).all())
            aImg = aImg[3:-4]
            aImgList = []
            aImgList = aImg.split("\',), (\'")
            aImg = aImgList[-1]

            aWt = str(db.session.query(After.aWeight).filter(After.userid == g.user, After.img2 == aImg).all())
            aWt = aWt[3:-4]
            aWtList = []
            aWtList = aWt.split("\',), (\'")
            aWt = aWtList[-1]

            aDt = str(db.session.query(After.aDate).filter(After.userid == g.user, After.img2 == aImg).all())
            aDt = aDt[3:-4]
            aDtList = []
            aDtList = aDt.split("\',), (\'")
            aDt = aDtList[-1]

            aImg = os.path.join(relPath, aImg)

            return render_template('progression/progression.html', bImg=dImg, bWt=default, bDt=default, aImg=aImg, aWt=aWt, aDt=aDt, reflections = reflections)
    else:
        if image2 == 0:
            # here only image1 rendered
            g.user = current_user.get_id()

            bImg = str(db.session.query(Before.img1).filter(Before.userid == g.user).all())
            bImg = bImg[3:-4]
            bImgList = []
            bImgList = bImg.split("\',), (\'")
            bImg = bImgList[-1]

            bWt = str(db.session.query(Before.bWeight).filter(Before.userid == g.user, Before.img1 == bImg).all())
            bWt = bWt[3:-4]
            bWtList = []
            bWtList = bWt.split("\',), (\'")
            bWt = bWtList[-1]

            bDt = str(db.session.query(Before.bDate).filter(Before.userid == g.user, Before.img1 == bImg).all())
            bDt = bDt[3:-4]
            bDtList = []
            bDtList = bDt.split("\',), (\'")
            bDt = bDtList[-1]

            bImg = os.path.join(relPath, bImg)

            return render_template('progression/progression.html', bImg=bImg, bWt=bWt, bDt=bDt, aImg=dImg, aWt=default, aDt=default, reflections = reflections)
        else:
            # here both images rendered
            g.user = current_user.get_id()

            bImg = str(db.session.query(Before.img1).filter(Before.userid == g.user).all())
            bImg = bImg[3:-4]
            bImgList = []
            bImgList = bImg.split("\',), (\'")
            bImg = bImgList[-1]
            bWt = str(db.session.query(Before.bWeight).filter(Before.userid == g.user, Before.img1 == bImg).all())
            bWt = bWt[3:-4]
            bWtList = []
            bWtList = bWt.split("\',), (\'")
            bWt = bWtList[-1]
            bDt = str(db.session.query(Before.bDate).filter(Before.userid == g.user, Before.img1 == bImg).all())
            bDt = bDt[3:-4]
            bDtList = []
            bDtList = bDt.split("\',), (\'")
            bDt = bDtList[-1]

            aImg = str(db.session.query(After.img2).filter(After.userid == g.user).all())
            aImg = aImg[3:-4]
            aImgList = []
            aImgList = aImg.split("\',), (\'")
            aImg = aImgList[-1]
            aWt = str(db.session.query(After.aWeight).filter(After.userid == g.user, After.img2 == aImg).all())
            aWt = aWt[3:-4]
            aWtList = []
            aWtList = aWt.split("\',), (\'")
            aWt = aWtList[-1]
            aDt = str(db.session.query(After.aDate).filter(After.userid == g.user, After.img2 == aImg).all())
            aDt = aDt[3:-4]
            aDtList = []
            aDtList = aDt.split("\',), (\'")
            aDt = aDtList[-1]

            bImg = os.path.join(relPath, bImg)
            aImg = os.path.join(relPath, aImg)

            return render_template('progression/progression.html', bImg=bImg, bWt=bWt, bDt=bDt, aImg=aImg, aWt=aWt, aDt=aDt, reflections = reflections)

# Allows for the adding of a reflection for view later
@app.route('/progression/addReflection',  methods=['GET', 'POST'])
@login_required
def addReflection():
    form = ReflectionForm()
    g.user = current_user.get_id()

    if form.validate_on_submit():
        new_reflection = Reflection(userid = g.user, date = form.date.data, reflection = form.reflection.data)
        db.session.add(new_reflection)
        db.session.commit()

        return redirect(url_for('progression'))
    return render_template('progression/addReflection.html', form=form)

# Allows for selection of reflection in a dropdown within progression and viewing
@app.route('/reflectionSelect', methods=['POST'])
def reflectionSelect():
    if request.method == 'POST':
        date = request.form["ref"]

        g.user = current_user.get_id()
        Date = db.session.query(Reflection.date).filter(Reflection.userid == g.user, Reflection.date == date).one()
        Date = str(Date)
        Date = Date.replace("(\'","")
        Date = Date.replace("\',)","")

        Ref = db.session.query(Reflection.reflection).filter(Reflection.userid == g.user, Reflection.date == date).one()
        Ref = str(Ref)
        Ref = Ref[2:]
        Ref = Ref[0:-3]


        print(Date,file=sys.stderr)
        print(Ref,file=sys.stderr)

        date = Date
        reflection = Ref

        return render_template('progression/viewReflection.html', date=date, reflection=reflection)
    return render_template('progression/progression.html')

# allows adding of the before image and data
@app.route("/AddImage1", methods=['GET', 'POST'])
def AddImage1():
    global image1
    form = Image1Form()
    g.user = current_user.get_id()
    if form.validate_on_submit():

        # save the image locally
        imgAll = form.pic1.data
        picName = secure_filename(imgAll.filename)
        imgAll.save(os.path.join(UPLOAD_FOLDER, picName))

        # just get the filename from the image for database
        new_image = Before(userid = g.user, img1 = picName, bWeight = form.bWeight.data,\
        bDate = form.bDate.data)
        db.session.add(new_image)
        db.session.commit()
        image1 = 1
        return redirect(url_for('progression'))
    return render_template('progression/AddImage1.html', form=form)

# allows adding of the after image and data
@app.route("/AddImage2", methods=['GET', 'POST'])
def AddImage2():
    global image2
    form = Image2Form()
    g.user = current_user.get_id()
    if form.validate_on_submit():

        # save the image locally
        imgAll = form.pic2.data
        picName = secure_filename(imgAll.filename)
        imgAll.save(os.path.join(UPLOAD_FOLDER, picName))

        # just get the filename from the image for database
        new_image = After(userid = g.user, img2 = picName, aWeight = form.aWeight.data,\
        aDate = form.aDate.data)
        db.session.add(new_image)
        db.session.commit()
        image2 = 1
        return redirect(url_for('progression'))
    return render_template('progression/AddImage2.html', form=form)
