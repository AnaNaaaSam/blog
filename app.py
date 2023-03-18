from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager,login_user,UserMixin,login_required,logout_user,current_user,AnonymousUserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = '12345'
with app.app_context():
    db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer,nullable = False)

class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200),nullable = False,unique = True)
    email = db.Column(db.String(200),nullable = False,unique = True)
    password = db.Column(db.String(200),nullable = False)



@app.route('/')
def index():
    tasks = content.query.order_by(content.date_created).all()

    try:
        if current_user.id == 1:
            return render_template('home.html',tasks=tasks,admin=True,Users=Users)
    except:
        pass
    return render_template('home.html',tasks=tasks,admin=False,Users=Users)


    


@app.route('/makepost', methods=['GET', 'POST'])
@login_required
def makepost():

    if request.method == 'POST':
        task_content = request.form['content']
        task_tcontent = request.form['tcontent']
        task_user_id = current_user.id
        new_task = content(text=task_content,user_id = task_user_id,title = task_tcontent)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            flash ('We had a problem adding your content')
            return redirect('/')
    if request.method == 'GET':
        return(render_template('makepost.html'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task = content.query.get_or_404(id)
    if current_user.id == task.user_id or current_user.id == 1 :
        try:
            db.session.delete(task)
            db.session.commit()
            return redirect('/')
        except:
            flash ('We had a problem deleting your content')
            return redirect('/')
    else:
        flash('You Dont Have This Permision')
        return redirect('/')

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']

        user = Users.query.filter_by(email = email).first()
        
        if not user:
            flash('Error!')
            return redirect('/login')
        else:
            if password != user.password:
                flash('Error!')
                return redirect('/login')          
              
        login_user(user)
        return redirect('/dashboard')
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        task_username = request.form['username']
        task_email = request.form['email']
        task_password = request.form['psw']


        try:
            db.session.add(Users(username = task_username,email = task_email,password = task_password))

            db.session.commit()
            return redirect('/login')
        except:
            flash ('We had a problem adding your user')
            return redirect('/signup')

    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():

    c1 = content.query.filter_by(user_id = current_user.id).all()
    return render_template('dashboard.html',tasks=c1,Users = Users)


@app.errorhandler(401)
def un(error):
    flash('You Must Log In')
    return redirect('/login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)