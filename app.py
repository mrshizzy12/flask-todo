from flask import Flask, render_template, redirect, url_for, flash, request, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import secrets
import os
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from wtforms.fields import StringField, BooleanField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from decorator import login_required

basedir = os.path.abspath(os.path.dirname(__file__))

''' create flask application instance '''
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "db.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['BOOTSTRAP_BTN_STYLE'] = 'success'
app.config['BOOTSTRAP_BTN_SIZE'] = 'md'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True


''' flask extensions '''
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db, render_as_batch=True)



''' Database model class '''
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, index=True, nullable=False)
    _password = db.Column(db.String(30), nullable=False)
    todolists = db.relationship('TodoList', backref='user', lazy='dynamic', cascade='all, delete')
    
    @property
    def password(self):
        raise AttributeError('password is not a readeable field')
    
    @password.setter
    def password(self, unhashed_password):
        self._password = generate_password_hash(unhashed_password)
        
    def check_password(self, unhased_password):
        return check_password_hash(self._password, unhased_password)
    
    def __repr__(self) -> str:
        return f'{self.username}'
    

class TodoList(db.Model):
    __tablename__ = 'todolists'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('Item', backref='todos', lazy='dynamic', cascade='all, delete')
    
    
    def __repr__(self) -> str:
        return f'{self.name}'

class Item(db.Model):
    __tablename__ ='items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(300))
    complete = db.Column(db.Boolean, default=False)
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'))

    def __repr__(self) -> str:
        return f'{self.text}'
    
 
''' flask wtf class '''   
class CreateTodoForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=200)])
    complete = BooleanField(validators=[Optional()])
    
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('submit')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('User already exists, please choose use a different username.')
  
        
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


''' custom errorhandlers '''    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

@app.errorhandler(500)
def page_not_found(e):
    db.session.rollback()
    return render_template('500.html'), 500
 
 

@app.route('/index/<int:id>', methods=["GET", 'POST'])
@login_required
def index(id):
    uid = session.get('user')
    user = User.query.get(uid)
    todo = user.todolists.filter_by(id=id).first_or_404()
    if request.method == 'POST':
        if request.form.get('save'):
            for item in todo.items.all():
                if request.form.get('c' + str(item.id)) == 'clicked':
                    item.complete = True
                else:
                    item.complete = False
                db.session.commit()
            flash('item(s) updated', 'info')
            return redirect(url_for('index', id=todo.id))
        elif request.form.get('newItem'):
            txt = request.form.get('new')
            
            if len(txt) > 2:
                item = Item(text=txt, complete=False)
                db.session.add(item)
                todo.items.append(item)
                db.session.commit()
                flash('new item added to the list', 'success')
                return redirect(url_for('index', id=todo.id))
            else:
                db.session.rollback()
                flash('error adding new item, please try again', 'danger')
                return redirect(url_for('index', id=todo.id))
    return render_template('index.html', todo=todo)



@app.route('/create/', methods=['GET','POST'])
@login_required
def create():
    form = CreateTodoForm()
    if form.validate_on_submit():
        t = TodoList(name=form.name.data, user_id=session.get('user'))
        db.session.add(t)
        db.session.commit()
        flash('New Todo was created', 'success')
        return redirect(url_for('view'))
    return render_template('create.html', form=form)



@app.get('/view/')
@login_required
def view():
    user = session.get('user')
    todo = User.query.get(user)
    return render_template('view.html', todo=todo)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged-in'):
        return redirect(url_for('view'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registration successfull', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged-in'):
        return redirect(url_for('view'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            session['user'] = user.id
            session['logged-in'] = True
            flash(f'welcome {user.username}', 'success')
            return redirect(url_for('view'))
    return render_template('login.html', form=form)


@app.get('/logout')
def logout():
    session.pop('user')
    session.pop('logged-in')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)