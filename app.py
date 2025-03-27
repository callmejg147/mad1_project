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

##---- MODELS ----##
class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    fname = db.Column(db.String(100), nullable = False)
    lname = db.Column(db.String(100), nullable = False)
    dob = db.Column(db.String, nullable = False)
    email = db.Column(db.String(200), nullable = False, unique = True)
    qualification = db.Column(db.String(200), nullable = True)
    username = db.Column(db.String(100), nullable = False, unique = True )
    password = db.Column(db.String(50), nullable = False)
    admin = db.Column(db.Boolean, default = False, nullable = False)
    flagged = db.Column(db.Boolean, default = False, nullable = False)
    subs = db.relationship('Subjects', secondary = 'enrollment', backref = 'enrolledSubs' )
    
class Subjects(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(150), nullable = False)
    usrs = db.relationship('Users', secondary = 'enrollment', backref = 'enrolledUsrs' )
    chaps = db.relationship('Chapters', backref = 'chapter')
    
class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, unique=False)
    completed = db.Column(db.Boolean, default = False, nullable = False )
# enrollment = db.Table(
#     "enrollment",
#     db.Column("student_id", db.Integer, db.ForeignKey("users.id")),
#     db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id")),
# )

class Chapters(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.String(500), nullable = False)
    sub_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), unique = False, nullable = True)
    sub = db.relationship('Subjects', backref = 'subject')
    
class Questions(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String(500), nullable = False)
    option1 = db.Column(db.String(100), nullable = False)
    option2 = db.Column(db.String(100), nullable = False)
    option3 = db.Column(db.String(100), nullable = False)
    option4 = db.Column(db.String(100), nullable = False)
    correct = db.Column(db.String(100), nullable = False)
    

with app.app_context():
    db.create_all()


##---- VIEWS ----##
@app.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html')
            
###############################################################  
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
            
###############################################################          
@app.route('/login_user', methods = ['GET','POST'])
def login_usr():
    if request.method == 'POST':
        user = Users.query.filter_by(username = request.form.get('usrnm')).first()
        # print(user)
        if user:
            if user.password == hashlib.md5(request.form.get('pswd').encode('utf-8')).hexdigest():
                login_user(user)
                flash('Successfully logged in.')
                return redirect('/user_dash')
            else:
                flash('Wrong credentials')
                return redirect('/')
        else:
            flash('User does not exist')
            return redirect('/')
@app.route('/admin_login', methods = ['GET','POST'])
def login_admin():
    if request.method == 'POST':
        user = Users.query.filter_by(username = request.form.get('usrnm')).first()
        # print(user)
        if user.admin:
            if user.password == hashlib.md5(request.form.get('pswd').encode('utf-8')).hexdigest():
                login_user(user)
                flash('Successfully logged in.')
                return redirect('/admin_dash')
            else:
                flash('Wrong credentials')
                return redirect('/')
        else:
            flash('User not admin')
            return redirect('/')
@app.route('/logout_user', methods = ['GET','POST'])
def logout_usr():
    logout_user()
    return redirect('/')
            
###############################################################  
@login_required
@app.route('/admin_dash',methods = ['GET', 'POST'])
def admin_view():
    if current_user.admin:
        return render_template('admin_dash.html')
@login_required
@app.route('/user_dash',methods = ['GET', 'POST'])
def user_view():
    if not current_user.admin:
        return render_template('dashboard.html')
            
###############################################################  
@app.route('/subjects', methods = ['GET','POST'])
def subjects_view():
    all_subs = Subjects.query.all()
    return render_template('subjects.html', subs = all_subs)  
@login_required
@app.route('/add_subject', methods = ['POST'])
def add_sub():
    if request.method == 'POST':      
        sub = Subjects(name = request.form.get('name'),
                        description = request.form.get('desc'))
        
        if current_user.admin :
            db.session.add(sub)
            db.session.commit()
            flash('Subject added succesfully.')
            return redirect('/subjects')         
@login_required
@app.route('/edit_subject/<int:sid>', methods = ['GET','POST'])
def edit_sub(sid):
    if request.method == 'POST':      
        sub = Subjects.query.get(sid)

        if current_user.admin :  
            print(request.form.get('desc'),request.form.get('name'))
            sub.name = request.form.get('name')
            sub.description = request.form.get('desc')
            
            db.session.commit()
            return redirect('/subjects')     
@login_required
@app.route('/delete_subject/<int:sid>', methods = ['GET','POST'])
def delete_sub(sid):    
        sub = Subjects.query.get(sid)

        if current_user.admin :
            db.session.delete(sub)
            db.session.commit()
            return redirect('/subjects')
            
############################################################### 

@login_required
@app.route('/chapters/<int:sid>', methods = ['GET','POST'])
def chapters_view(sid):
    sub = Subjects.query.get(sid)
    chapters = Chapters.query.filter_by(sub_id = sid).all()
    return render_template('chapters.html', chaps = chapters, sub = sub)            
@login_required
@app.route('/add_chapter/<int:sid>', methods = ['POST'])
def add_chap(sid):
    if request.method == 'POST':      
        chap = Chapters(title = request.form.get('title'),
                        content = request.form.get('points'),
                        sub_id = sid)
        
        if current_user.admin :
            db.session.add(chap)
            db.session.commit()
            flash('Chapter added succesfully.')
            return redirect(f'/chapters/{sid}')
@login_required
@app.route('/edit_chapter/<int:cid>', methods = ['GET','POST'])
def edit_chap(cid):
    if request.method == 'POST':      
        chap = Chapters.query.get(cid)

        if current_user.admin :  
            chap.title = request.form.get('title')
            chap.content = request.form.get('points')
            
            db.session.commit()
            return redirect(f'/chapters/{chap.sub_id}')     
@login_required
@app.route('/delete_chapter/<int:cid>', methods = ['GET','POST'])
def delete_chap(cid):    
        chap = Chapters.query.get(cid)

        if current_user.admin :
            db.session.delete(chap)
            db.session.commit()
            return redirect(f'/chapters/{chap.sub_id}')
        
            
# @login_required
# @app.route('/user_dashboard', methods = ['GET', 'POST'])
# def user_dash():
#     return render_template('dashboard.html')







        



