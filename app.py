from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import hashlib

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = 't1isismysEcretkEy'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# models
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    fname = db.Column(db.String(100), nullable = True)
    lname = db.Column(db.String(100), nullable = True)
    dob = db.Column(db.String, nullable = True)
    email = db.Column(db.String(200), nullable = True, unique = True)
    qualification = db.Column(db.String(200), nullable = True)
    username = db.Column(db.String(100), nullable = True, unique = True )
    password = db.Column(db.String(50), nullable = True)



with app.app_context():
    db.create_all()

@app.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/register_user', methods = ['GET','POST'])
def add_user():
    if request.method == 'POST':
        uname =request.form.get('usrnm')
        mail = request.form.get('email')
        if Users.query.filter_by(username=uname).first() == None:
            if Users.query.filter_by(email=mail).first() == None:
                if request.form.get('pswd') == request.form.get('cpswd'):
                    user = Users(fname = request.form.get('fname'),
                                 lname = request.form.get('lname'),
                                 email = request.form.get('email'),
                                 dob = request.form.get('dob'),
                                 qualification = request.form.get('quali'),
                                 username = request.form.get('usrnm'),
                                 password = hashlib.md5(request.form.get('pswd').encode('utf-8')).hexdigest())
                    db.session.add(user)
                    db.session.commit()
                    return redirect('/')
                else:
                    print('passwords do not match')
            else:
                print('user email already exist')
        else:
            print('username already exist')
            

            
@app.route('/login_user', methods = ['GET','POST'])
def login_usr():
    if request.method == 'POST':
        user = Users.query.filter_by(username = request.form.get('usrnm')).first()
        # print(user)
        if user:
            if user.password == hashlib.md5(request.form.get('pswd').encode('utf-8')).hexdigest():
                login_user(user)
                flash('Successfully logged in.')
                return redirect('/user_dashboard')
            else:
                flash('Wrong credentials')
                return redirect('/')
        else:
            flash('User does not exist')
            return redirect('/')
                
            
@app.route('/logout_user', methods = ['GET','POST'])
def logout_usr():
    logout_user()
    return redirect('/')
        
            
@login_required
@app.route('/user_dashboard', methods = ['GET', 'POST'])
def user_dash():
    return render_template('dashboard.html')







        



