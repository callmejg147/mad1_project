from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import hashlib
from functions import score_calc

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
    chaps = db.relationship('Chapters', secondary = 'quiz', backref = 'quizChapters')
    name = db.Column(db.String(100))
    

    
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
    ques = db.relationship('Questions', backref = 'question')
    usrs = db.relationship('Users', secondary = 'quiz', backref = 'quizUser')
    
class Questions(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String(500), nullable = False)
    option1 = db.Column(db.String(100), nullable = False)
    option2 = db.Column(db.String(100), nullable = False)
    option3 = db.Column(db.String(100), nullable = False)
    option4 = db.Column(db.String(100), nullable = False)
    correct = db.Column(db.String(100), nullable = False)
    chap_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), unique = False, nullable = False)
    chap = db.relationship('Chapters', backref = 'chaps')
    
class Quiz(db.Model):
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False, unique = False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable = False, unique = False)
    score = db.Column(db.Integer, nullable = True)
    

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
                                 name = request.form.get('fname') + ' ' + request.form.get('lname'),
                                 email = request.form.get('email'),
                                 dob = request.form.get('dob'),
                                 qualification = request.form.get('quali'),
                                 username = request.form.get('usrnm'),
                                 password = hashlib.md5(request.form.get('pswd').encode('utf-8')).hexdigest())
                    db.session.add(user)
                    db.session.commit()
                    
                    flash('Registered successfully. Please login to continue.')
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
        subs = Subjects.query.all()
        population = {}
        for sub in subs:
            population[sub.name] = len(sub.usrs)

        subjects = list(population.keys()) 
        s_count = list(population.values())
        ucount = len(list(Users.query.filter_by(admin=0).all()))
        scount = len(list(Subjects.query.all()))
        fcount = len(list(Users.query.filter_by(flagged=1).all()))
        return render_template('admin_dash.html', 
                               subjects = subjects, 
                               students = s_count, 
                               ucount = ucount, 
                               scount = scount, 
                               fcount = fcount)
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
    quizs = Quiz.query.filter_by(student_id=current_user.id)
    ques = Questions.query.all()
    return render_template('chapters.html', chaps = chapters, sub = sub, ques = ques, quizs = quizs)            
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
            
############################################################### 
# @login_required
# @app.route('/chapters/<int:sid>', methods = ['GET','POST'])
# def chapters_view(sid):
#     sub = Subjects.query.get(sid)
#     chapters = Chapters.query.filter_by(sub_id = sid).all()
#     return render_template('chapters.html', chaps = chapters, sub = sub)
@login_required
@app.route('/questions/<int:cid>', methods = ['GET','POST'])
def questions_view(cid):
    chap = Chapters.query.get(cid)
    subject = chap.sub.name
    ques = Questions.query.filter_by(chap_id = cid).all()
    return render_template('questions.html', ques = ques, subject = subject, chap = chap)        
@login_required
@app.route('/add_question/<int:cid>', methods = ['POST'])
def add_ques(cid):
    if request.method == 'POST':      
        question = Questions(ques = request.form.get('ques'),
                        option1 = request.form.get('option1'),
                        option2 = request.form.get('option2'),
                        option3 = request.form.get('option3'),
                        option4 = request.form.get('option4'),
                        correct = request.form.get('ans'),
                        chap_id = cid)
        chap = Chapters.query.get(cid)
        if current_user.admin :
            db.session.add(question)
            db.session.commit()
            flash('Question added succesfully.')
            return redirect(f'/chapters/{chap.sub_id}')
@login_required
@app.route('/edit_question/<int:qid>', methods = ['GET','POST'])
def edit_ques(qid):
    if request.method == 'POST':      
        question = Questions.query.get(qid)

        if current_user.admin :  
            question.ques = request.form.get('ques')
            question.option1 = request.form.get('option1')
            question.option2 = request.form.get('option2')
            question.option3 = request.form.get('option3')
            question.option4 = request.form.get('option4')
            question.correct = request.form.get('ans')
            
            db.session.commit()
            return redirect(f'/questions/{question.chap_id}')     
@login_required
@app.route('/delete_question/<int:qid>', methods = ['GET','POST'])
def delete_ques(qid):    
        question = Questions.query.get(qid)
        cid = question.chap_id
        if current_user.admin :
            db.session.delete(question)
            db.session.commit()
            return redirect(f'/questions/{cid}')
        
        
@login_required
@app.route('/users', methods = ['GET','POST'])
def users_view():
    if current_user.admin:
        users = Users.query.filter_by(admin=0).all()
        quizs = Quiz.query.all()
        return render_template('users.html', users=users, quizs = quizs)

@app.route('/flag_user/<int:uid>', methods = ['POST','GET'])
def flag_usr(uid):
    user = Users.query.get(uid)
    if current_user.admin:
        user.flagged = True
        db.session.commit()
        return redirect('/users')
    
    
@login_required
@app.route('/enroll/<int:uid>/<int:sid>', methods = ['GET','POST'])
def enroll_user(uid, sid):
    enroll = Enrollment(student_id = uid,
                        subject_id = sid)
    if current_user.is_authenticated:
        db.session.add(enroll)
        db.session.commit()
        return redirect('/subjects')
    
    
@login_required
@app.route('/submit_quiz/<int:cid>/<int:uid>', methods = ['GET','POST'])
def submit_q(cid, uid):
    chap = Chapters.query.get(cid)

    
    total = score_calc(chap)
    q = Quiz.query.filter(Quiz.student_id == uid, Quiz.chapter_id == cid).first()
    if q is not None:
        if q.score <= total:
            q.score = total
            db.session.commit()
            return redirect(f'/chapters/{chap.sub_id}')
        else:
            return redirect(f'/chapters/{chap.sub_id}')
    else:
        quizz = Quiz(student_id = uid,
                 chapter_id = cid,
                 score = total)
        # print(chap)
        db.session.add(quizz)
        db.session.commit()
        return redirect(f'/chapters/{chap.sub_id}')
    
@app.route('/search_subjects', methods = ['GET','POST'])
def search_sub():
    if request.method == 'POST':
        searched = request.form.get('keyword')
        subs = Subjects.query.filter(Subjects.name.like('%' + searched + '%')).all()

        return render_template('subjects.html', subs = subs)
    
@app.route('/search_students', methods = ['GET','POST'])
def search_stud():
    if request.method == 'POST':
        searched = request.form.get('keyword')
        studs = Users.query.filter(Users.name.like('%' + searched + '%'), Users.admin == 0).all()
        print(searched, studs)
        return render_template('users.html', users = studs)
        
# @login_required
# @app.route('/user_dashboard', methods = ['GET', 'POST'])
# def user_dash():
#     return render_template('dashboard.html')







        



