from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app import login_manager
from flask_login import UserMixin

### START OF USER MODEL CODE + AUXILIARY FUNCTIONS ###

# Class for the User DB table
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False, index = True)
    password = db.Column(db.String, nullable = False)
    authenticated = db.Column(db.Boolean, default = False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object."""
    return User.query.get(user_id)

### END OF USER MODEL CODE ###

### START OF CODE FOR ALL OTHER MODELS ###

# Here is where the other database models will be


class Before(db.Model):
    __tablename__ = 'before'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    img1 = db.Column(db.String(), nullable=True)
    bWeight = db.Column(db.Text, nullable=False)
    bDate = db.Column(db.Text, nullable=False)

class After(db.Model):
    __tablename__ = 'after'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    img2 = db.Column(db.String(), nullable=True)
    aWeight = db.Column(db.Text, nullable=False)
    aDate = db.Column(db.Text, nullable=False)

class Reflection(db.Model):
    __tablename__ = 'reflection'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    reflection = db.Column(db.String(200), nullable=False)

class Workout(db.Model):
    __tablename__ = 'workout'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    workout = db.Column(db.String(200), nullable=False)
    bodypart = db.Column(db.String(200), nullable=False)

class Calories(db.Model):
    __tablename__ = 'calories'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    cal4day = db.Column(db.Integer, nullable=False)

class Bmr(db.Model):
    __tablename__ = 'bmr'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    bmr = db.Column(db.Integer, nullable=False)
